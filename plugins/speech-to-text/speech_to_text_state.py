import logging
import requests
import json
import os
import tempfile
from datetime import datetime
from urllib.parse import urlparse
from .base_state import BaseState

logger = logging.getLogger(__name__)

class SpeechToTextState(BaseState):
    """
    Stato per convertire audio in testo utilizzando OpenAI Whisper API.
    Supporta diversi formati audio, lingue multiple e rilevamento automatico della lingua.
    """
    state_type = "speech_to_text"
    
    # Formati audio supportati da Whisper
    SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.flac', '.ogg'}
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB limite Whisper API
    
    def execute(self, variables):
        logger.debug(f"Esecuzione dello stato 'speech_to_text' {self.name} con configurazione: {self.state_config}")
        
        # Parametri obbligatori
        api_key = self.format_recursive(self.state_config.get("api_key"), variables)
        audio_file = self.format_recursive(self.state_config.get("audio_file"), variables)
        
        if not api_key:
            logger.error("api_key è obbligatorio per il plugin Speech-to-Text")
            return self._handle_error("API key mancante", variables)
        
        if not audio_file:
            logger.error("audio_file è obbligatorio per il plugin Speech-to-Text")
            return self._handle_error("File audio mancante", variables)
        
        # Parametri opzionali con valori di default
        language = self.format_recursive(self.state_config.get("language", "auto"), variables)
        model = self.format_recursive(self.state_config.get("model", "whisper-1"), variables)
        response_format = self.format_recursive(self.state_config.get("response_format", "json"), variables)
        temperature = float(self.state_config.get("temperature", 0.0))
        workspace_path = self.format_recursive(self.state_config.get("workspace_path", "workspace"), variables)
        prompt = self.format_recursive(self.state_config.get("prompt"), variables)
        
        # Crea la cartella workspace se non esiste
        try:
            os.makedirs(workspace_path, exist_ok=True)
            logger.info(f"Cartella workspace creata/verificata: {workspace_path}")
        except Exception as e:
            logger.error(f"Errore nella creazione della cartella workspace: {e}")
            return self._handle_error(f"Errore workspace: {e}", variables)
        
        # Gestione del file audio (locale o remoto)
        local_file_path = None
        temp_file = None
        
        try:
            if self._is_url(audio_file):
                logger.info(f"Download file audio da URL: {audio_file}")
                local_file_path, temp_file = self._download_audio_file(audio_file, workspace_path)
            else:
                local_file_path = audio_file
                if not os.path.exists(local_file_path):
                    return self._handle_error(f"File audio non trovato: {local_file_path}", variables)
            
            # Validazione del file
            validation_result = self._validate_audio_file(local_file_path)
            if not validation_result["valid"]:
                return self._handle_error(validation_result["error"], variables)
            
            # Preparazione parametri per l'API Whisper
            transcription_params = {
                "model": model,
                "response_format": response_format,
                "temperature": temperature
            }
            
            # Aggiungi lingua se non è auto-detect
            if language and language.lower() != "auto":
                transcription_params["language"] = language
            
            # Aggiungi prompt se specificato
            if prompt:
                transcription_params["prompt"] = prompt
            
            # Chiamata all'API Whisper
            logger.info(f"Inizio trascrizione con Whisper API - File: {os.path.basename(local_file_path)}")
            start_time = datetime.now()
            
            result = self._transcribe_audio(local_file_path, api_key, transcription_params)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Trascrizione completata in {processing_time:.2f} secondi")
            
            # Preparazione del risultato
            file_info = validation_result["file_info"]
            transcription_result = self._prepare_result(
                result, 
                file_info, 
                processing_time, 
                transcription_params
            )
            
            # Salva il risultato nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = transcription_result
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except Exception as e:
            error_msg = f"Errore durante la trascrizione: {e}"
            logger.error(error_msg)
            return self._handle_error(error_msg, variables)
            
        finally:
            # Cleanup del file temporaneo se necessario
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                    logger.debug(f"File temporaneo rimosso: {temp_file}")
                except Exception as e:
                    logger.warning(f"Impossibile rimuovere file temporaneo {temp_file}: {e}")
    
    def _is_url(self, path):
        """Verifica se il percorso è un URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _download_audio_file(self, url, workspace_path):
        """Scarica un file audio da URL."""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determina l'estensione del file dall'URL o Content-Type
            parsed_url = urlparse(url)
            file_extension = os.path.splitext(parsed_url.path)[1].lower()
            
            if not file_extension or file_extension not in self.SUPPORTED_FORMATS:
                content_type = response.headers.get('content-type', '').lower()
                if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                    file_extension = '.mp3'
                elif 'audio/wav' in content_type:
                    file_extension = '.wav'
                elif 'audio/ogg' in content_type:
                    file_extension = '.ogg'
                else:
                    file_extension = '.mp3'  # Default
            
            # Crea file temporaneo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_audio_{timestamp}{file_extension}"
            temp_path = os.path.join(workspace_path, temp_filename)
            
            # Scarica il file
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"File audio scaricato: {temp_path}")
            return temp_path, temp_path
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Errore nel download del file audio: {e}")
        except Exception as e:
            raise Exception(f"Errore generico nel download: {e}")
    
    def _validate_audio_file(self, file_path):
        """Valida il file audio."""
        try:
            if not os.path.exists(file_path):
                return {"valid": False, "error": f"File non trovato: {file_path}"}
            
            # Verifica estensione
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension not in self.SUPPORTED_FORMATS:
                return {
                    "valid": False, 
                    "error": f"Formato non supportato: {file_extension}. Formati supportati: {', '.join(self.SUPPORTED_FORMATS)}"
                }
            
            # Verifica dimensione
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                return {
                    "valid": False,
                    "error": f"File troppo grande: {file_size / (1024*1024):.1f}MB. Limite: 25MB"
                }
            
            if file_size == 0:
                return {"valid": False, "error": "File vuoto"}
            
            # Informazioni del file
            file_info = {
                "filename": os.path.basename(file_path),
                "file_size": file_size,
                "format": file_extension[1:],  # Rimuovi il punto
                "size_mb": round(file_size / (1024*1024), 2)
            }
            
            return {"valid": True, "file_info": file_info}
            
        except Exception as e:
            return {"valid": False, "error": f"Errore nella validazione del file: {e}"}
    
    def _transcribe_audio(self, file_path, api_key, params):
        """Effettua la trascrizione usando OpenAI Whisper API."""
        try:
            # Importa OpenAI client
            try:
                from openai import OpenAI
            except ImportError:
                raise Exception("Libreria 'openai' non installata. Esegui: pip install openai>=1.0.0")
            
            # Inizializza client OpenAI
            client = OpenAI(api_key=api_key)
            
            # Apri il file audio
            with open(file_path, 'rb') as audio_file:
                # Effettua la trascrizione
                response = client.audio.transcriptions.create(
                    file=audio_file,
                    **params
                )
            
            return response
            
        except Exception as e:
            if "authentication" in str(e).lower():
                raise Exception(f"Errore di autenticazione OpenAI: {e}")
            elif "quota" in str(e).lower():
                raise Exception(f"Quota API OpenAI esaurita: {e}")
            elif "rate limit" in str(e).lower():
                raise Exception(f"Limite di rate OpenAI raggiunto: {e}")
            else:
                raise Exception(f"Errore API OpenAI: {e}")
    
    def _prepare_result(self, whisper_response, file_info, processing_time, params):
        """Prepara il risultato finale della trascrizione."""
        result = {
            "success": True,
            "processing_time": round(processing_time, 2),
            "model_used": params.get("model", "whisper-1"),
            "file_info": file_info,
            "parameters": {
                "language": params.get("language", "auto-detect"),
                "response_format": params.get("response_format", "json"),
                "temperature": params.get("temperature", 0.0)
            }
        }
        
        # Gestione diversi formati di risposta
        response_format = params.get("response_format", "json")
        
        if response_format == "text":
            result["text"] = whisper_response
            result["word_count"] = len(whisper_response.split()) if whisper_response else 0
            
        elif response_format in ["srt", "vtt"]:
            result["subtitles"] = whisper_response
            result["format"] = response_format
            
        elif response_format == "verbose_json":
            # Risposta dettagliata con segmenti e timestamp
            if hasattr(whisper_response, 'text'):
                result["text"] = whisper_response.text
                result["language"] = getattr(whisper_response, 'language', 'unknown')
                result["duration"] = getattr(whisper_response, 'duration', None)
                result["segments"] = getattr(whisper_response, 'segments', [])
                result["word_count"] = len(whisper_response.text.split()) if whisper_response.text else 0
            else:
                result["text"] = str(whisper_response)
                result["word_count"] = len(str(whisper_response).split())
                
        else:  # json format (default)
            if hasattr(whisper_response, 'text'):
                result["text"] = whisper_response.text
                result["word_count"] = len(whisper_response.text.split()) if whisper_response.text else 0
            else:
                result["text"] = str(whisper_response)
                result["word_count"] = len(str(whisper_response).split())
        
        return result
    
    def _handle_error(self, error_message, variables):
        """Gestisce gli errori e salva le informazioni se necessario."""
        logger.error(error_message)
        
        # Salva l'errore nelle variabili se specificato
        output_key = self.state_config.get("output")
        if output_key:
            variables[output_key] = {
                "success": False,
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
        
        return self.state_config.get("error_transition", "end")
