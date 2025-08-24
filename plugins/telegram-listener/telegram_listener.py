"""
Telegram Listener Plugin per IntellyHub
Ascolta messaggi in arrivo da bot Telegram e triggera workflow automaticamente
"""

import requests
import time
import logging
import threading
from typing import Dict, Any, List, Optional
from yaml import safe_load
from flow.flow import FlowDiagram
from flow.listeners.base_listener import BaseListener

logger = logging.getLogger(__name__)

class TelegramListener(BaseListener):
    """
    Listener per messaggi Telegram in arrivo.
    
    Utilizza long polling per ascoltare messaggi e triggerare workflow automaticamente.
    Supporta filtraggio per chat_id, tipi di messaggio e configurazioni avanzate.
    """
    
    listener_type = "telegram-listener"
    
    def __init__(self, event_config: Dict[str, Any], global_context: Optional[Dict[str, Any]] = None):
        super().__init__(event_config, global_context)
        
        # Configurazione del bot
        self.bot_token = event_config.get("bot_token")
        if not self.bot_token:
            raise ValueError("bot_token è obbligatorio per il Telegram Listener")
        
        # Configurazioni di filtraggio
        self.allowed_chat_ids = event_config.get("allowed_chat_ids", [])
        self.message_types = event_config.get("message_types", ["text"])
        
        # Configurazioni di polling
        self.polling_interval = event_config.get("polling_interval", 2)
        self.timeout = event_config.get("timeout", 30)
        self.ignore_old_messages = event_config.get("ignore_old_messages", True)
        
        # Stato interno
        self._running = False
        self._thread = None
        self._last_update_id = 0
        self._api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        logger.info(f"🤖 Telegram Listener inizializzato per bot token: ...{self.bot_token[-10:]}")
    
    def setup(self):
        """Setup del listener - verifica la connessione al bot"""
        try:
            # Test della connessione con getMe
            response = requests.get(f"{self._api_base_url}/getMe", timeout=10)
            response.raise_for_status()
            
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_data = bot_info["result"]
                logger.info(f"✅ Connessione al bot Telegram verificata: @{bot_data.get('username', 'unknown')}")
                
                # Se ignoriamo i messaggi vecchi, ottieni l'ultimo update_id
                if self.ignore_old_messages:
                    self._get_latest_update_id()
                    
            else:
                raise Exception(f"Errore API Telegram: {bot_info.get('description', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Errore durante il setup del Telegram Listener: {e}")
            raise
    
    def listen(self, config_file: str):
        """
        Metodo principale del listener - avvia il polling dei messaggi
        
        Args:
            config_file: Path del file di configurazione YAML
        """
        logger.info(f"🚀 Avvio Telegram Listener - polling ogni {self.polling_interval}s")
        
        # Setup iniziale
        self.setup()
        
        # Avvia il thread di polling
        self._running = True
        self._thread = threading.Thread(target=self._polling_loop, args=(config_file,))
        self._thread.daemon = True
        self._thread.start()
        
        try:
            # Mantieni il thread principale attivo
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Interruzione ricevuta, fermando il listener...")
            self.stop()
    
    def stop(self):
        """Ferma il listener"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("🛑 Telegram Listener fermato")
    
    def _polling_loop(self, config_file: str):
        """Loop principale di polling per i messaggi"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self._running:
            try:
                # Ottieni gli aggiornamenti da Telegram
                updates = self._get_updates()
                
                if updates:
                    logger.debug(f"📨 Ricevuti {len(updates)} aggiornamenti")
                    
                    for update in updates:
                        if not self._running:
                            break
                        
                        # Processa ogni messaggio
                        self._process_update(update, config_file)
                        
                        # Aggiorna l'ultimo update_id processato
                        self._last_update_id = max(self._last_update_id, update.get("update_id", 0))
                
                # Reset del contatore errori se tutto va bene
                consecutive_errors = 0
                
                # Pausa prima del prossimo polling
                time.sleep(self.polling_interval)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ Errore nel polling Telegram (tentativo {consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"💥 Troppi errori consecutivi ({consecutive_errors}), fermando il listener")
                    self._running = False
                    break
                
                # Pausa più lunga in caso di errore
                time.sleep(min(self.polling_interval * consecutive_errors, 30))
    
    def _get_updates(self) -> List[Dict[str, Any]]:
        """Ottiene gli aggiornamenti da Telegram API"""
        params = {
            "offset": self._last_update_id + 1,
            "timeout": self.timeout,
            "limit": 100
        }
        
        response = requests.get(
            f"{self._api_base_url}/getUpdates",
            params=params,
            timeout=self.timeout + 5
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            return result.get("result", [])
        else:
            raise Exception(f"Errore API Telegram: {result.get('description', 'Unknown error')}")
    
    def _get_latest_update_id(self):
        """Ottiene l'ultimo update_id per ignorare messaggi vecchi"""
        try:
            params = {"offset": -1, "limit": 1}
            response = requests.get(f"{self._api_base_url}/getUpdates", params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok") and result.get("result"):
                self._last_update_id = result["result"][0].get("update_id", 0)
                logger.info(f"📍 Ultimo update_id impostato a: {self._last_update_id}")
        except Exception as e:
            logger.warning(f"⚠️ Impossibile ottenere l'ultimo update_id: {e}")
    
    def _process_update(self, update: Dict[str, Any], config_file: str):
        """Processa un singolo aggiornamento da Telegram"""
        try:
            # Estrai il messaggio dall'update
            message = update.get("message")
            if not message:
                logger.debug("📭 Update senza messaggio, ignorato")
                return
            
            # Estrai informazioni dal messaggio
            message_data = self._extract_message_data(message)
            
            # Applica filtri
            if not self._should_process_message(message_data):
                logger.debug(f"🚫 Messaggio filtrato: {message_data.get('telegram_message_type')} da {message_data.get('telegram_chat_id')}")
                return
            
            logger.info(f"📨 Processando messaggio da {message_data.get('telegram_user_first_name', 'Unknown')} ({message_data.get('telegram_chat_id')})")
            
            # Triggera il workflow
            self._trigger_workflow(message_data, config_file)
            
        except Exception as e:
            logger.error(f"❌ Errore nel processare update: {e}")
    
    def _extract_message_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Estrae i dati dal messaggio Telegram e li formatta per il workflow"""
        chat = message.get("chat", {})
        user = message.get("from", {})
        
        # Determina il tipo di messaggio
        message_type = "text"
        message_text = message.get("text", "")
        
        if message.get("photo"):
            message_type = "photo"
            message_text = message.get("caption", "")
        elif message.get("document"):
            message_type = "document"
            message_text = message.get("caption", "")
        elif message.get("audio"):
            message_type = "audio"
        elif message.get("video"):
            message_type = "video"
            message_text = message.get("caption", "")
        elif message.get("voice"):
            message_type = "voice"
        elif message.get("sticker"):
            message_type = "sticker"
        elif message.get("location"):
            message_type = "location"
        elif message.get("contact"):
            message_type = "contact"
        
        return {
            "telegram_message_text": message_text,
            "telegram_chat_id": str(chat.get("id", "")),
            "telegram_user_id": str(user.get("id", "")),
            "telegram_message_id": str(message.get("message_id", "")),
            "telegram_user_first_name": user.get("first_name", ""),
            "telegram_user_last_name": user.get("last_name", ""),
            "telegram_user_username": user.get("username", ""),
            "telegram_message_type": message_type,
            "telegram_message_date": str(message.get("date", "")),
            "telegram_chat_type": chat.get("type", ""),
            "telegram_chat_title": chat.get("title", "")
        }
    
    def _should_process_message(self, message_data: Dict[str, Any]) -> bool:
        """Determina se il messaggio deve essere processato in base ai filtri"""
        
        # Filtro per chat_id autorizzati
        if self.allowed_chat_ids:
            chat_id = message_data.get("telegram_chat_id")
            if chat_id and int(chat_id) not in self.allowed_chat_ids:
                return False
        
        # Filtro per tipi di messaggio
        message_type = message_data.get("telegram_message_type", "text")
        if message_type not in self.message_types:
            return False
        
        return True
    
    def _trigger_workflow(self, message_data: Dict[str, Any], config_file: str):
        """Triggera il workflow con i dati del messaggio"""
        try:
            # Carica la configurazione del workflow
            with open(config_file, 'r', encoding='utf-8') as file:
                config = safe_load(file)
            
            # Crea e avvia il workflow
            flow = FlowDiagram(config, self.global_context)
            
            # Inietta le variabili del messaggio
            flow.variables.update(message_data)
            
            # Inietta anche le variabili globali se presenti
            if self.global_context:
                flow.variables.update(self.global_context)
            
            logger.info(f"🚀 Avvio workflow per messaggio: '{message_data.get('telegram_message_text', '')[:50]}...'")
            
            # Esegui il workflow
            flow.run()
            
            logger.info("✅ Workflow completato con successo")
            
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione del workflow: {e}")
            raise
