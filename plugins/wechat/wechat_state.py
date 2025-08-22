"""
WeChat Work Plugin per IntellyHub
Permette di inviare messaggi tramite API WeChat Work
"""

import requests
import logging
import time
import json
from typing import Dict, Any, Optional
from flow.states.base_state import BaseState

logger = logging.getLogger(__name__)

class WeChatState(BaseState):
    """
    Stato per inviare messaggi tramite API WeChat Work
    
    Configurazione YAML:
    ```yaml
    send_wechat:
      state_type: wechat
      corp_id: "{WECHAT_CORP_ID}"
      corp_secret: "{WECHAT_CORP_SECRET}"
      agent_id: "{WECHAT_AGENT_ID}"
      to_user: "{WECHAT_USER_ID}"  # opzionale
      to_party: "1"                # opzionale
      to_tag: "tag1"               # opzionale
      message: "Testo del messaggio"
      message_type: "text"         # text, textcard, markdown
      safe: 0                      # 0=normale, 1=confidenziale
      output: "wechat_result"      # opzionale
      success_transition: next_state
      error_transition: handle_error
    ```
    """
    
    state_type = "wechat"
    
    # URL base per API WeChat Work
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
    
    def __init__(self, name: str, config: Dict[str, Any], global_context: Dict[str, Any]):
        super().__init__(name, config, global_context)
        self.corp_id = self.state_config.get('corp_id')
        self.corp_secret = self.state_config.get('corp_secret')
        self.agent_id = self.state_config.get('agent_id')
        self.to_user = self.state_config.get('to_user', '@all')
        self.to_party = self.state_config.get('to_party', '')
        self.to_tag = self.state_config.get('to_tag', '')
        self.message = self.state_config.get('message', '')
        self.message_type = self.state_config.get('message_type', 'text')
        self.safe = self.state_config.get('safe', 0)
        self._access_token = None
        self._token_expires_at = 0
        
    def execute(self, variables: Dict[str, Any]) -> str:
        """
        Invia il messaggio WeChat Work
        
        Args:
            variables: Variabili del contesto
            
        Returns:
            Nome dello stato successivo
        """
        try:
            # Risolvi placeholder nelle variabili
            resolved_corp_id = self.format_recursive(self.corp_id, variables)
            resolved_corp_secret = self.format_recursive(self.corp_secret, variables)
            resolved_agent_id = self.format_recursive(self.agent_id, variables)
            resolved_to_user = self.format_recursive(self.to_user, variables)
            resolved_to_party = self.format_recursive(self.to_party, variables)
            resolved_to_tag = self.format_recursive(self.to_tag, variables)
            resolved_message = self.format_recursive(self.message, variables)
            
            logger.info(f"💬 Invio messaggio WeChat Work tramite agente {resolved_agent_id}")
            
            # Ottieni access token
            access_token = self._get_access_token(resolved_corp_id, resolved_corp_secret)
            if not access_token:
                logger.error("❌ Impossibile ottenere access token WeChat Work")
                return self._handle_error(variables, "Impossibile ottenere access token")
            
            # Prepara il messaggio
            message_data = self._prepare_message(
                resolved_agent_id,
                resolved_to_user,
                resolved_to_party,
                resolved_to_tag,
                resolved_message
            )
            
            # Invia il messaggio
            result = self._send_message(access_token, message_data)
            
            if result.get('errcode') == 0:
                logger.info(f"✅ Messaggio WeChat Work inviato con successo")
                
                # Salva info nella variabile di output se specificata
                output_key = self.state_config.get('output')
                if output_key:
                    variables[output_key] = {
                        'success': True,
                        'errcode': result.get('errcode'),
                        'errmsg': result.get('errmsg'),
                        'msgid': result.get('msgid'),
                        'response_code': result.get('response_code'),
                        'timestamp': int(time.time())
                    }
                    
                return self.state_config.get('success_transition', 
                                           self.state_config.get('transition'))
            else:
                error_msg = f"Errore WeChat Work: {result.get('errmsg', 'Errore sconosciuto')} (Code: {result.get('errcode')})"
                logger.error(f"❌ {error_msg}")
                return self._handle_error(variables, error_msg, result)
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout nell'invio del messaggio WeChat Work")
            return self._handle_error(variables, "Timeout nella richiesta")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore di rete WeChat Work: {e}")
            return self._handle_error(variables, f"Errore di rete: {e}")
            
        except Exception as e:
            logger.error(f"❌ Errore inaspettato WeChat Work: {e}")
            return self._handle_error(variables, f"Errore inaspettato: {e}")
    
    def _get_access_token(self, corp_id: str, corp_secret: str) -> Optional[str]:
        """
        Ottiene l'access token per l'API WeChat Work
        """
        # Controlla se il token è ancora valido
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        
        try:
            url = f"{self.BASE_URL}/gettoken"
            params = {
                'corpid': corp_id,
                'corpsecret': corp_secret
            }
            
            logger.debug("🔑 Richiesta access token WeChat Work")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errcode') == 0:
                self._access_token = result.get('access_token')
                expires_in = result.get('expires_in', 7200)  # Default 2 ore
                self._token_expires_at = time.time() + expires_in - 300  # Rinnova 5 min prima
                
                logger.debug(f"✅ Access token ottenuto, scade tra {expires_in} secondi")
                return self._access_token
            else:
                logger.error(f"❌ Errore ottenimento token: {result.get('errmsg')} (Code: {result.get('errcode')})")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore nella richiesta del token: {e}")
            return None
    
    def _prepare_message(self, agent_id: str, to_user: str, to_party: str, 
                        to_tag: str, message: str) -> Dict[str, Any]:
        """
        Prepara il payload del messaggio secondo l'API WeChat Work
        """
        # Costruisci i destinatari
        touser = to_user if to_user else ""
        toparty = to_party if to_party else ""
        totag = to_tag if to_tag else ""
        
        # Se nessun destinatario specificato, invia a tutti
        if not touser and not toparty and not totag:
            touser = "@all"
        
        # Prepara il contenuto del messaggio in base al tipo
        if self.message_type == "text":
            msgtype = "text"
            content = {"content": message}
        elif self.message_type == "markdown":
            msgtype = "markdown"
            content = {"content": message}
        elif self.message_type == "textcard":
            # Per textcard, il messaggio dovrebbe essere in formato JSON
            try:
                textcard_data = json.loads(message)
                msgtype = "textcard"
                content = textcard_data
            except json.JSONDecodeError:
                # Fallback a text se il JSON non è valido
                logger.warning("⚠️ Formato textcard non valido, uso text")
                msgtype = "text"
                content = {"content": message}
        else:
            msgtype = "text"
            content = {"content": message}
        
        message_data = {
            "touser": touser,
            "toparty": toparty,
            "totag": totag,
            "msgtype": msgtype,
            "agentid": int(agent_id),
            msgtype: content,
            "safe": self.safe
        }
        
        return message_data
    
    def _send_message(self, access_token: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invia il messaggio tramite API WeChat Work
        """
        url = f"{self.BASE_URL}/message/send"
        params = {'access_token': access_token}
        
        logger.debug(f"📤 Invio messaggio: {json.dumps(message_data, ensure_ascii=False)}")
        
        response = requests.post(
            url, 
            params=params, 
            json=message_data, 
            timeout=30,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        response.raise_for_status()
        
        return response.json()
    
    def _handle_error(self, variables: Dict[str, Any], error_msg: str, 
                     api_result: Optional[Dict[str, Any]] = None) -> str:
        """
        Gestisce gli errori e salva le informazioni se richiesto
        """
        output_key = self.state_config.get('output')
        if output_key:
            error_data = {
                'success': False,
                'error': error_msg,
                'timestamp': int(time.time())
            }
            
            if api_result:
                error_data.update({
                    'errcode': api_result.get('errcode'),
                    'errmsg': api_result.get('errmsg')
                })
            
            variables[output_key] = error_data
        
        return self.state_config.get('error_transition', 'error')
    
    def validate_config(self) -> bool:
        """
        Valida la configurazione dello stato
        """
        required_fields = ['corp_id', 'corp_secret', 'agent_id', 'message']
        missing_fields = [field for field in required_fields 
                         if not self.state_config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campi mancanti in wechat state: {', '.join(missing_fields)}")
        
        # Valida message_type
        valid_types = ['text', 'textcard', 'markdown']
        if self.message_type not in valid_types:
            raise ValueError(f"message_type deve essere uno di: {', '.join(valid_types)}")
        
        # Valida safe
        if self.safe not in [0, 1]:
            raise ValueError("safe deve essere 0 o 1")
            
        return True
