import logging
import requests
import json
import os
from datetime import datetime
from .base_state import BaseState

logger = logging.getLogger(__name__)

class TextToSpeechState(BaseState):
    """
    Stato per convertire testo in audio utilizzando ElevenLabs API.
    Genera file MP3 nella cartella workspace con supporto per diverse voci e lingue.
    """
    state_type = "text_to_speech"
    
    def execute(self, variables):
        logger.debug(f"Esecuzione dello stato 'text_to_speech' {self.name} con configurazione: {self.state_config}")
        
        # Parametri obbligatori
        api_key = self.format_recursive(self.state_config.get("api_key"), variables)
        text = self.format_recursive(self.state_config.get("text"), variables)
        
        if not api_key:
            logger.error("api_key è obbligatorio per il plugin Text-to-Speech")
            return self.state_config.get("error_transition", "end")
        
        if not text:
            logger.error("text è obbligatorio per il plugin Text-to-Speech")
            return self.state_config.get("error_transition", "end")
        
        # Parametri opzionali con valori di default
        voice_id = self.format_recursive(self.state_config.get("voice_id", "21m00Tcm4TlvDq8ikWAM"), variables)
        model_id = self.format_recursive(self.state_config.get("model_id", "eleven_monolingual_v1"), variables)
        filename_prefix = self.format_recursive(self.state_config.get("filename_prefix"), variables)
        workspace_path = self.format_recursive(self.state_config.get("workspace_path", "workspace"), variables)
        
        # Impostazioni della voce (opzionali)
        voice_settings = self.state_config.get("voice_settings", {})
        if voice_settings:
            voice_settings = self.format_recursive(voice_settings, variables)
        else:
            # Impostazioni di default
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        
        # Crea la cartella workspace se non esiste
        try:
            os.makedirs(workspace_path, exist_ok=True)
            logger.info(f"Cartella workspace creata/verificata: {workspace_path}")
        except Exception as e:
            logger.error(f"Errore nella creazione della cartella workspace: {e}")
            return self.state_config.get("error_transition", "end")
        
        # Genera il nome del file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if filename_prefix:
            filename = f"{filename_prefix}_{timestamp}.mp3"
        else:
            filename = f"{timestamp}.mp3"
        
        filepath = os.path.join(workspace_path, filename)
        
        # Costruisci il payload per l'API ElevenLabs
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }
        
        # Headers per l'API
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # URL dell'API ElevenLabs
        api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        try:
            logger.info(f"Invio richiesta TTS a ElevenLabs per voce {voice_id}")
            logger.debug(f"Testo da convertire: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            # Effettua la chiamata POST all'API ElevenLabs
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Salva il file audio
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"File audio generato con successo: {filepath}")
            
            # Calcola la dimensione del file
            file_size = os.path.getsize(filepath)
            
            # Salva il risultato nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "workspace_path": workspace_path,
                    "file_size": file_size,
                    "voice_id": voice_id,
                    "model_id": model_id,
                    "text_length": len(text),
                    "message": "Audio generato con successo"
                }
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Errore HTTP durante la chiamata a ElevenLabs: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - Dettagli: {error_details}"
                except:
                    error_msg += f" - Status Code: {e.response.status_code}"
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            logger.error(error_msg)
            
            # Salva l'errore nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": error_msg,
                    "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None,
                    "voice_id": voice_id,
                    "text_length": len(text)
                }
            
            return self.state_config.get("error_transition", "end")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Errore di connessione durante la chiamata a ElevenLabs: {e}"
            logger.error(error_msg)
            
            # Salva l'errore nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": error_msg,
                    "voice_id": voice_id,
                    "text_length": len(text)
                }
            
            return self.state_config.get("error_transition", "end")
            
        except Exception as e:
            error_msg = f"Errore generico durante la generazione TTS: {e}"
            logger.error(error_msg)
            
            # Salva l'errore nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": error_msg,
                    "voice_id": voice_id,
                    "text_length": len(text)
                }
            
            return self.state_config.get("error_transition", "end")
