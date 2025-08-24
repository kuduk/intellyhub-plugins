"""
Telegram Listener Plugin per IntellyHub
Ascolta messaggi in arrivo da bot Telegram e triggera workflow automaticamente
"""

import requests
import time
import logging
import threading
import os
import uuid
from datetime import datetime
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
    
    listener_type = "telegram"
    
    def __init__(self, event_config: Dict[str, Any], global_context: Optional[Dict[str, Any]] = None):
        super().__init__(event_config, global_context)
        
        # Configurazione del bot
        bot_token_raw = event_config.get("bot_token")
        if not bot_token_raw:
            raise ValueError("bot_token è obbligatorio per il Telegram Listener")
        
        # Formatta il bot_token con le variabili globali se presenti
        if global_context:
            self.bot_token = self.format_recursive(bot_token_raw, global_context)
        else:
            self.bot_token = bot_token_raw
        
        # Configurazioni di filtraggio
        self.allowed_chat_ids = event_config.get("allowed_chat_ids", [])
        self.message_types = event_config.get("message_types", ["text"])
        
        # Configurazioni di polling
        self.polling_interval = event_config.get("polling_interval", 2)
        self.timeout = event_config.get("timeout", 30)
        self.ignore_old_messages = event_config.get("ignore_old_messages", True)
        
        # Configurazioni per messaggi vocali
        self.download_voice = event_config.get("download_voice", True)
        self.voice_download_path = event_config.get("voice_download_path", "workspace")
        self.transcribe_voice = event_config.get("transcribe_voice", True)
        
        # Crea la cartella workspace se non esiste
        if self.download_voice:
            os.makedirs(self.voice_download_path, exist_ok=True)
        
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
    
    def _download_voice_file(self, voice_data: Dict[str, Any], chat_id: str, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Scarica un file vocale da Telegram e lo salva localmente
        
        Args:
            voice_data: Dati del messaggio vocale da Telegram
            chat_id: ID della chat
            message_id: ID del messaggio
            
        Returns:
            Dict con informazioni sul file scaricato o None se errore
        """
        try:
            file_id = voice_data.get("file_id")
            if not file_id:
                logger.error("❌ File ID vocale mancante")
                return None
            
            # Ottieni informazioni sul file
            file_info_response = requests.get(
                f"{self._api_base_url}/getFile",
                params={"file_id": file_id},
                timeout=10
            )
            file_info_response.raise_for_status()
            
            file_info = file_info_response.json()
            if not file_info.get("ok"):
                logger.error(f"❌ Errore ottenendo info file: {file_info.get('description')}")
                return None
            
            file_path = file_info["result"].get("file_path")
            file_size = file_info["result"].get("file_size", 0)
            
            if not file_path:
                logger.error("❌ File path mancante")
                return None
            
            # Genera nome file univoco
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = os.path.splitext(file_path)[1] or ".ogg"
            filename = f"voice_{timestamp}_{chat_id}_{message_id}_{unique_id}{file_extension}"
            local_path = os.path.join(self.voice_download_path, filename)
            
            # Scarica il file
            download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            logger.info(f"🎤 Scaricamento vocale: {filename}")
            
            download_response = requests.get(download_url, timeout=30)
            download_response.raise_for_status()
            
            # Salva il file
            with open(local_path, 'wb') as f:
                f.write(download_response.content)
            
            # Informazioni sul file scaricato
            file_info_result = {
                "file_path": local_path,
                "file_name": filename,
                "file_size": file_size,
                "duration": voice_data.get("duration", 0),
                "mime_type": voice_data.get("mime_type", "audio/ogg"),
                "download_success": True
            }
            
            logger.info(f"✅ Vocale scaricato: {filename} ({file_size} bytes)")
            return file_info_result
            
        except Exception as e:
            logger.error(f"❌ Errore scaricamento vocale: {e}")
            return {
                "download_success": False,
                "error": str(e)
            }
    
    def _transcribe_voice_file(self, file_path: str) -> Optional[str]:
        """
        Trascrive un file vocale usando speech-to-text
        
        Args:
            file_path: Percorso del file vocale
            
        Returns:
            Testo trascritto o None se errore
        """
        try:
            # Prova prima con speech_recognition se disponibile
            try:
                import speech_recognition as sr
                
                recognizer = sr.Recognizer()
                
                # Converti OGG in WAV se necessario
                audio_file = file_path
                if file_path.endswith('.ogg'):
                    try:
                        from pydub import AudioSegment
                        audio = AudioSegment.from_ogg(file_path)
                        wav_path = file_path.replace('.ogg', '.wav')
                        audio.export(wav_path, format="wav")
                        audio_file = wav_path
                    except ImportError:
                        logger.warning("⚠️ pydub non disponibile, provo con file OGG originale")
                
                # Trascrivi
                with sr.AudioFile(audio_file) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language='it-IT')
                    
                logger.info(f"🎯 Trascrizione completata: '{text[:50]}...'")
                return text
                
            except ImportError:
                logger.warning("⚠️ speech_recognition non disponibile")
            except sr.UnknownValueError:
                logger.warning("⚠️ Impossibile riconoscere l'audio")
                return "[Audio non riconoscibile]"
            except sr.RequestError as e:
                logger.warning(f"⚠️ Errore servizio riconoscimento: {e}")
                return "[Errore trascrizione]"
            
            # Fallback: prova con whisper se disponibile
            try:
                import whisper
                
                model = whisper.load_model("base")
                result = model.transcribe(file_path, language="it")
                text = result["text"].strip()
                
                logger.info(f"🎯 Trascrizione Whisper completata: '{text[:50]}...'")
                return text
                
            except ImportError:
                logger.warning("⚠️ whisper non disponibile")
            
            # Se nessun metodo funziona
            logger.warning("⚠️ Nessun sistema di trascrizione disponibile")
            return "[Trascrizione non disponibile]"
            
        except Exception as e:
            logger.error(f"❌ Errore trascrizione: {e}")
            return f"[Errore trascrizione: {e}]"
    
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
        
        # Variabili base del messaggio
        base_data = {
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
        
        if message.get("photo"):
            message_type = "photo"
            message_text = message.get("caption", "")
            base_data["telegram_message_text"] = message_text
            base_data["telegram_message_type"] = message_type
        elif message.get("document"):
            message_type = "document"
            message_text = message.get("caption", "")
            base_data["telegram_message_text"] = message_text
            base_data["telegram_message_type"] = message_type
        elif message.get("audio"):
            message_type = "audio"
            base_data["telegram_message_type"] = message_type
        elif message.get("video"):
            message_type = "video"
            message_text = message.get("caption", "")
            base_data["telegram_message_text"] = message_text
            base_data["telegram_message_type"] = message_type
        elif message.get("voice"):
            message_type = "voice"
            base_data["telegram_message_type"] = message_type
            
            # Gestione speciale per i messaggi vocali
            if self.download_voice:
                voice_data = message.get("voice", {})
                chat_id = base_data["telegram_chat_id"]
                message_id = base_data["telegram_message_id"]
                
                # Scarica il file vocale
                voice_file_info = self._download_voice_file(voice_data, chat_id, message_id)
                
                if voice_file_info and voice_file_info.get("download_success"):
                    # Aggiungi informazioni sul file vocale
                    base_data.update({
                        "telegram_voice_file_path": voice_file_info["file_path"],
                        "telegram_voice_file_name": voice_file_info["file_name"],
                        "telegram_voice_file_size": str(voice_file_info["file_size"]),
                        "telegram_voice_duration": str(voice_file_info["duration"]),
                        "telegram_voice_mime_type": voice_file_info["mime_type"]
                    })
                    
                    # Trascrizione del vocale se abilitata
                    if self.transcribe_voice:
                        logger.info("🎯 Avvio trascrizione vocale...")
                        transcription = self._transcribe_voice_file(voice_file_info["file_path"])
                        if transcription:
                            base_data["telegram_voice_transcription"] = transcription
                            base_data["telegram_message_text"] = transcription  # Usa la trascrizione come testo
                            logger.info(f"✅ Trascrizione: '{transcription[:50]}...'")
                        else:
                            base_data["telegram_voice_transcription"] = "[Trascrizione fallita]"
                    
                else:
                    # Errore nel download
                    base_data.update({
                        "telegram_voice_file_path": "",
                        "telegram_voice_file_name": "",
                        "telegram_voice_file_size": "0",
                        "telegram_voice_duration": str(voice_data.get("duration", 0)),
                        "telegram_voice_mime_type": voice_data.get("mime_type", "audio/ogg"),
                        "telegram_voice_transcription": "[Download fallito]"
                    })
            
        elif message.get("sticker"):
            message_type = "sticker"
            base_data["telegram_message_type"] = message_type
        elif message.get("location"):
            message_type = "location"
            base_data["telegram_message_type"] = message_type
        elif message.get("contact"):
            message_type = "contact"
            base_data["telegram_message_type"] = message_type
        
        return base_data
    
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
            
            # Per i listener, il start_state è sempre il primo stato definito
            # o "start" se non specificato diversamente
            start_state = config.get("start_state", "start")
            
            # Crea e avvia il workflow
            flow = FlowDiagram(config, self.global_context, start_state=start_state)
            
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
