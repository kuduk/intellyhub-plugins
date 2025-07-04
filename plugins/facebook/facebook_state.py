import logging
import requests
import json
from datetime import datetime, timedelta
from .base_state import BaseState

logger = logging.getLogger(__name__)

class FacebookState(BaseState):
    """
    Stato per pubblicare post su Facebook utilizzando l'API Graph.
    Supporta post di testo, link e scheduling.
    """
    state_type = "facebook"
    
    def execute(self, variables):
        logger.debug(f"Esecuzione dello stato 'facebook' {self.name} con configurazione: {self.state_config}")
        
        # Parametri obbligatori
        access_token = self.format_recursive(self.state_config.get("access_token"), variables)
        page_id = self.format_recursive(self.state_config.get("page_id"), variables)
        message = self.format_recursive(self.state_config.get("message", ""), variables)
        
        if not access_token:
            logger.error("access_token è obbligatorio per il plugin Facebook")
            return self.state_config.get("error_transition", "end")
        
        if not page_id:
            logger.error("page_id è obbligatorio per il plugin Facebook")
            return self.state_config.get("error_transition", "end")
        
        # Parametri opzionali
        link = self.format_recursive(self.state_config.get("link"), variables)
        scheduled_publish_time = self.format_recursive(self.state_config.get("scheduled_publish_time"), variables)
        
        # Costruisci il payload per l'API Facebook
        post_data = {
            "access_token": access_token
        }
        
        # Aggiungi il messaggio se presente
        if message:
            post_data["message"] = message
        
        # Aggiungi il link se presente
        if link:
            post_data["link"] = link
        
        # Gestisci lo scheduling
        if scheduled_publish_time:
            try:
                # Converti la data in timestamp Unix se è una stringa
                if isinstance(scheduled_publish_time, str):
                    # Supporta diversi formati di data
                    try:
                        # Formato ISO: 2024-01-15T10:30:00
                        scheduled_dt = datetime.fromisoformat(scheduled_publish_time.replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            # Formato: 2024-01-15 10:30:00
                            scheduled_dt = datetime.strptime(scheduled_publish_time, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # Formato: 15/01/2024 10:30
                            scheduled_dt = datetime.strptime(scheduled_publish_time, "%d/%m/%Y %H:%M")
                    
                    scheduled_timestamp = int(scheduled_dt.timestamp())
                else:
                    scheduled_timestamp = int(scheduled_publish_time)
                
                post_data["scheduled_publish_time"] = scheduled_timestamp
                post_data["published"] = "false"  # Necessario per i post programmati
                
                logger.info(f"Post programmato per: {datetime.fromtimestamp(scheduled_timestamp)}")
                
            except Exception as e:
                logger.error(f"Errore nel parsing della data di scheduling: {e}")
                return self.state_config.get("error_transition", "end")
        
        # URL dell'API Facebook Graph
        api_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        
        try:
            # Effettua la chiamata POST all'API Facebook
            response = requests.post(api_url, data=post_data)
            response.raise_for_status()
            
            result = response.json()
            post_id = result.get("id")
            
            if post_id:
                logger.info(f"Post pubblicato con successo su Facebook. ID: {post_id}")
                
                # Salva l'ID del post nelle variabili se specificato
                output_key = self.state_config.get("output")
                if output_key:
                    variables[output_key] = {
                        "post_id": post_id,
                        "success": True,
                        "message": "Post pubblicato con successo",
                        "scheduled": bool(scheduled_publish_time)
                    }
                
                return self.state_config.get("success_transition", self.state_config.get("transition"))
            else:
                logger.error("Risposta API Facebook non contiene l'ID del post")
                return self.state_config.get("error_transition", "end")
                
        except requests.exceptions.HTTPError as e:
            error_msg = f"Errore HTTP durante la pubblicazione su Facebook: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - Dettagli: {error_details}"
                except:
                    error_msg += f" - Status Code: {e.response.status_code}"
            
            logger.error(error_msg)
            
            # Salva l'errore nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": error_msg,
                    "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
                }
            
            return self.state_config.get("error_transition", "end")
            
        except Exception as e:
            error_msg = f"Errore generico durante la pubblicazione su Facebook: {e}"
            logger.error(error_msg)
            
            # Salva l'errore nelle variabili se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": error_msg
                }
            
            return self.state_config.get("error_transition", "end")
