"""
Telegram Bot Plugin per IntellyHub
Permette di inviare messaggi tramite bot Telegram
"""

import requests
import logging
from typing import Dict, Any, Optional
from flow.states.base_state import BaseState

logger = logging.getLogger(__name__)

class TelegramState(BaseState):
    """
    Stato per inviare messaggi tramite bot Telegram
    
    Configurazione YAML:
    ```yaml
    send_telegram:
      state_type: telegram
      bot_token: "{TELEGRAM_BOT_TOKEN}"
      chat_id: "{TELEGRAM_CHAT_ID}"
      message: "Testo del messaggio"
      parse_mode: "HTML"  # opzionale: HTML, Markdown
      disable_notification: false  # opzionale
      transition: next_state
    ```
    """
    
    def __init__(self, name: str, config: Dict[str, Any], global_context: Dict[str, Any]):
        super().__init__(name, config, global_context)
        self.bot_token = self.config.get('bot_token')
        self.chat_id = self.config.get('chat_id')
        self.message = self.config.get('message', '')
        self.parse_mode = self.config.get('parse_mode', 'HTML')
        self.disable_notification = self.config.get('disable_notification', False)
        
    def execute(self, variables: Dict[str, Any]) -> str:
        """
        Invia il messaggio Telegram
        
        Args:
            variables: Variabili del contesto
            
        Returns:
            Nome dello stato successivo
        """
        try:
            # Risolvi placeholder nelle variabili
            resolved_bot_token = str(self.bot_token).format(**variables)
            resolved_chat_id = str(self.chat_id).format(**variables)
            resolved_message = str(self.message).format(**variables)
            
            # Costruisci l'URL dell'API Telegram
            url = f"https://api.telegram.org/bot{resolved_bot_token}/sendMessage"
            
            # Prepara il payload
            payload = {
                'chat_id': resolved_chat_id,
                'text': resolved_message,
                'parse_mode': self.parse_mode,
                'disable_notification': self.disable_notification
            }
            
            logger.info(f"📱 Invio messaggio Telegram a chat_id: {resolved_chat_id}")
            
            # Invia la richiesta
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                message_id = result['result']['message_id']
                logger.info(f"✅ Messaggio inviato con successo (ID: {message_id})")
                
                # Salva info nella variabile di output se specificata
                if self.config.get('output'):
                    variables[self.config['output']] = {
                        'success': True,
                        'message_id': message_id,
                        'chat_id': resolved_chat_id,
                        'timestamp': result['result']['date']
                    }
                    
                return self.config.get('success_transition', self.config.get('transition'))
            else:
                error_msg = result.get('description', 'Errore sconosciuto')
                logger.error(f"❌ Errore Telegram: {error_msg}")
                
                if self.config.get('output'):
                    variables[self.config['output']] = {
                        'success': False,
                        'error': error_msg
                    }
                    
                return self.config.get('error_transition', 'error')
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout nell'invio del messaggio Telegram")
            return self.config.get('error_transition', 'error')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore di rete Telegram: {e}")
            return self.config.get('error_transition', 'error')
            
        except Exception as e:
            logger.error(f"❌ Errore inaspettato: {e}")
            return self.config.get('error_transition', 'error')
    
    def validate_config(self) -> bool:
        """
        Valida la configurazione dello stato
        """
        required_fields = ['bot_token', 'chat_id', 'message']
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campi mancanti in telegram state: {', '.join(missing_fields)}")
            
        return True
