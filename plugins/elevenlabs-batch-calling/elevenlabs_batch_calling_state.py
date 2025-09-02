import logging
import requests
import json
from datetime import datetime
from .base_state import BaseState

logger = logging.getLogger(__name__)

class ElevenLabsBatchCallingState(BaseState):
    """
    Stato per gestire batch calls di ElevenLabs Conversational AI.
    Supporta la creazione, monitoraggio e gestione di campagne di chiamate automatizzate.
    
    Operazioni supportate:
    - submit: Crea un nuovo job di batch calling
    - get: Recupera informazioni su un batch job esistente  
    - list: Lista tutti i job di batch calling nel workspace
    """
    state_type = "elevenlabs_batch_calling"
    
    def execute(self, variables):
        logger.debug(f"Esecuzione dello stato 'elevenlabs_batch_calling' {self.name} con configurazione: {self.state_config}")
        
        # Parametro obbligatorio
        api_key = self.format_recursive(self.state_config.get("api_key"), variables)
        if not api_key:
            logger.error("api_key è obbligatorio per il plugin ElevenLabs Batch Calling")
            return self.state_config.get("error_transition", "end")
        
        # Determina l'operazione da eseguire
        operation = self.format_recursive(self.state_config.get("operation", "submit"), variables)
        
        logger.info(f"Esecuzione operazione '{operation}' per ElevenLabs Batch Calling")
        
        # Esegui l'operazione appropriata
        try:
            if operation == "submit":
                return self._submit_batch_call(api_key, variables)
            elif operation == "get":
                return self._get_batch_call(api_key, variables)
            elif operation == "list":
                return self._list_batch_calls(api_key, variables)
            else:
                logger.error(f"Operazione non supportata: {operation}")
                self._save_error_result(variables, f"Operazione non supportata: {operation}")
                return self.state_config.get("error_transition", "end")
                
        except Exception as e:
            error_msg = f"Errore durante l'esecuzione dell'operazione '{operation}': {e}"
            logger.error(error_msg)
            self._save_error_result(variables, error_msg)
            return self.state_config.get("error_transition", "end")
    
    def _submit_batch_call(self, api_key, variables):
        """Crea e sottomette un nuovo job di batch calling"""
        logger.info("Creazione nuovo batch call job")
        
        # Parametri obbligatori per submit
        call_name = self.format_recursive(self.state_config.get("call_name"), variables)
        agent_id = self.format_recursive(self.state_config.get("agent_id"), variables)
        agent_phone_number_id = self.format_recursive(self.state_config.get("agent_phone_number_id"), variables)
        recipients = self.state_config.get("recipients", [])
        
        # Validazione parametri obbligatori
        if not call_name:
            logger.error("call_name è obbligatorio per l'operazione 'submit'")
            self._save_error_result(variables, "call_name è obbligatorio per l'operazione 'submit'")
            return self.state_config.get("error_transition", "end")
        
        if not agent_id:
            logger.error("agent_id è obbligatorio per l'operazione 'submit'")
            self._save_error_result(variables, "agent_id è obbligatorio per l'operazione 'submit'")
            return self.state_config.get("error_transition", "end")
        
        if not agent_phone_number_id:
            logger.error("agent_phone_number_id è obbligatorio per l'operazione 'submit'")
            self._save_error_result(variables, "agent_phone_number_id è obbligatorio per l'operazione 'submit'")
            return self.state_config.get("error_transition", "end")
        
        if not recipients or len(recipients) == 0:
            logger.error("recipients è obbligatorio e non può essere vuoto per l'operazione 'submit'")
            self._save_error_result(variables, "recipients è obbligatorio e non può essere vuoto per l'operazione 'submit'")
            return self.state_config.get("error_transition", "end")
        
        # Processa i recipients (array nativo con oggetti annidati)
        formatted_recipients = []
        
        # I recipients devono essere un array di oggetti
        if not isinstance(recipients, list):
            logger.error("recipients deve essere un array di oggetti")
            self._save_error_result(variables, "recipients deve essere un array di oggetti")
            return self.state_config.get("error_transition", "end")
        
        # Processa ogni recipient con oggetti annidati
        for i, recipient in enumerate(recipients):
            if not isinstance(recipient, dict):
                logger.error(f"Recipient {i+1}: deve essere un oggetto, ricevuto {type(recipient)}")
                self._save_error_result(variables, f"Recipient {i+1}: deve essere un oggetto")
                return self.state_config.get("error_transition", "end")
            
            # Valida che esista phone_number (può essere annidato o diretto)
            phone_number = recipient.get("phone_number")
            if not phone_number:
                logger.error(f"Recipient {i+1}: manca il campo obbligatorio 'phone_number'")
                self._save_error_result(variables, f"Recipient {i+1}: manca il campo obbligatorio 'phone_number'")
                return self.state_config.get("error_transition", "end")
            
            # Processa l'oggetto recipient con tutte le sue proprietà annidate
            formatted_recipient = self._process_nested_recipient(recipient, variables, i+1)
            if formatted_recipient is None:
                return self.state_config.get("error_transition", "end")
            
            formatted_recipients.append(formatted_recipient)
        
        # Parametro opzionale
        scheduled_time_unix = self.state_config.get("scheduled_time_unix")
        if scheduled_time_unix is not None:
            scheduled_time_unix = self.format_recursive(scheduled_time_unix, variables)
            if isinstance(scheduled_time_unix, str) and scheduled_time_unix.isdigit():
                scheduled_time_unix = int(scheduled_time_unix)
        
        # Costruisci il payload
        payload = {
            "call_name": call_name,
            "agent_id": agent_id,
            "agent_phone_number_id": agent_phone_number_id,
            "recipients": formatted_recipients
        }
        
        # Aggiungi scheduled_time_unix solo se non è null/None
        if scheduled_time_unix is not None:
            payload["scheduled_time_unix"] = scheduled_time_unix
        
        # Headers per l'API
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # URL dell'API ElevenLabs
        api_url = "https://api.elevenlabs.io/v1/convai/batch-calling/submit"
        
        try:
            logger.info(f"Invio richiesta batch call per {len(formatted_recipients)} recipients")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Batch call creato con successo. ID: {result.get('id')}")
            
            # Salva il risultato nelle variabili se specificato
            self._save_success_result(variables, result, "submit")
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except requests.exceptions.HTTPError as e:
            return self._handle_http_error(e, variables, "submit")
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, variables, "submit")
    
    def _get_batch_call(self, api_key, variables):
        """Recupera informazioni dettagliate su un batch job esistente"""
        logger.info("Recupero informazioni batch call job")
        
        # Parametro obbligatorio per get
        batch_id = self.format_recursive(self.state_config.get("batch_id"), variables)
        
        if not batch_id:
            logger.error("batch_id è obbligatorio per l'operazione 'get'")
            self._save_error_result(variables, "batch_id è obbligatorio per l'operazione 'get'")
            return self.state_config.get("error_transition", "end")
        
        # Headers per l'API
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        # URL dell'API ElevenLabs
        api_url = f"https://api.elevenlabs.io/v1/convai/batch-calling/{batch_id}"
        
        try:
            logger.info(f"Recupero informazioni per batch ID: {batch_id}")
            
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Informazioni batch call recuperate. Status: {result.get('status')}")
            
            # Salva il risultato nelle variabili se specificato
            self._save_success_result(variables, result, "get")
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except requests.exceptions.HTTPError as e:
            return self._handle_http_error(e, variables, "get")
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, variables, "get")
    
    def _list_batch_calls(self, api_key, variables):
        """Lista tutti i job di batch calling nel workspace"""
        logger.info("Lista job di batch calling")
        
        # Parametri opzionali per list
        limit = self.state_config.get("limit", 100)
        last_doc = self.format_recursive(self.state_config.get("last_doc"), variables)
        
        # Costruisci i parametri della query
        params = {"limit": limit}
        if last_doc:
            params["last_doc"] = last_doc
        
        # Headers per l'API
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        # URL dell'API ElevenLabs
        api_url = "https://api.elevenlabs.io/v1/convai/batch-calling/workspace"
        
        try:
            logger.info(f"Lista batch calls con limite: {limit}")
            
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            batch_count = len(result.get("batch_calls", []))
            logger.info(f"Recuperati {batch_count} batch calls")
            
            # Salva il risultato nelle variabili se specificato
            self._save_success_result(variables, result, "list")
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except requests.exceptions.HTTPError as e:
            return self._handle_http_error(e, variables, "list")
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(e, variables, "list")
    
    def _save_success_result(self, variables, result, operation):
        """Salva il risultato di successo nelle variabili"""
        output_key = self.state_config.get("output")
        if output_key:
            enhanced_result = {
                "success": True,
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "data": result
            }
            
            # Aggiungi informazioni specifiche dell'operazione
            if operation == "submit":
                enhanced_result.update({
                    "batch_id": result.get("id"),
                    "status": result.get("status"),
                    "total_calls_scheduled": result.get("total_calls_scheduled"),
                    "message": f"Batch call '{result.get('name')}' creato con successo"
                })
            elif operation == "get":
                enhanced_result.update({
                    "batch_id": result.get("id"),
                    "status": result.get("status"),
                    "total_calls_dispatched": result.get("total_calls_dispatched"),
                    "total_calls_scheduled": result.get("total_calls_scheduled"),
                    "message": f"Informazioni batch call recuperate"
                })
            elif operation == "list":
                batch_calls = result.get("batch_calls", [])
                enhanced_result.update({
                    "batch_count": len(batch_calls),
                    "has_more": result.get("has_more", False),
                    "next_doc": result.get("next_doc"),
                    "message": f"Recuperati {len(batch_calls)} batch calls"
                })
            
            variables[output_key] = enhanced_result
            logger.debug(f"Risultato salvato in variabile '{output_key}'")
    
    def _save_error_result(self, variables, error_message):
        """Salva il risultato di errore nelle variabili"""
        output_key = self.state_config.get("output")
        if output_key:
            variables[output_key] = {
                "success": False,
                "error": error_message,
                "timestamp": datetime.now().isoformat(),
                "operation": self.state_config.get("operation", "unknown")
            }
            logger.debug(f"Errore salvato in variabile '{output_key}'")
    
    def _handle_http_error(self, e, variables, operation):
        """Gestisce errori HTTP dall'API ElevenLabs"""
        error_msg = f"Errore HTTP durante {operation}: {e}"
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
            error_result = {
                "success": False,
                "operation": operation,
                "error": error_msg,
                "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None,
                "timestamp": datetime.now().isoformat()
            }
            variables[output_key] = error_result
        
        return self.state_config.get("error_transition", "end")
    
    def _handle_request_error(self, e, variables, operation):
        """Gestisce errori di connessione"""
        error_msg = f"Errore di connessione durante {operation}: {e}"
        logger.error(error_msg)
        
        # Salva l'errore nelle variabili se specificato
        output_key = self.state_config.get("output")
        if output_key:
            variables[output_key] = {
                "success": False,
                "operation": operation,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        return self.state_config.get("error_transition", "end")
    
    def _process_nested_recipient(self, recipient, variables, recipient_index):
        """
        Processa un recipient con oggetti annidati, formattando ricorsivamente
        tutti i campi e appiattendo la struttura per l'API ElevenLabs
        """
        try:
            # Inizializza il recipient formattato con phone_number obbligatorio
            formatted_recipient = {
                "phone_number": self.format_recursive(recipient["phone_number"], variables)
            }
            
            # Processa contact_info se presente
            contact_info = recipient.get("contact_info", {})
            if contact_info and isinstance(contact_info, dict):
                for field in ["name", "company", "title", "department"]:
                    if field in contact_info:
                        # Per ElevenLabs API, questi possono essere campi diretti o andare in custom_data
                        value = self.format_recursive(contact_info[field], variables)
                        if field == "name":
                            formatted_recipient["name"] = value
                        else:
                            # Altri campi contact_info vanno in custom_data come JSON
                            if "custom_data" not in formatted_recipient:
                                formatted_recipient["custom_data"] = {}
                            formatted_recipient["custom_data"][field] = value
            
            # Processa preferences se presente  
            preferences = recipient.get("preferences", {})
            if preferences and isinstance(preferences, dict):
                # Language può essere un campo diretto se supportato dall'API
                if "language" in preferences:
                    language_value = self.format_recursive(preferences["language"], variables)
                    formatted_recipient["language"] = language_value
                
                # Altri campi preferences vanno in custom_data
                for field in ["timezone", "best_call_times", "blackout_dates"]:
                    if field in preferences:
                        if "custom_data" not in formatted_recipient:
                            formatted_recipient["custom_data"] = {}
                        formatted_recipient["custom_data"][field] = self.format_recursive(preferences[field], variables)
            
            # Processa metadata se presente
            metadata = recipient.get("metadata", {})
            if metadata and isinstance(metadata, dict):
                if "custom_data" not in formatted_recipient:
                    formatted_recipient["custom_data"] = {}
                
                # Tutti i campi metadata vanno in custom_data
                for field, value in metadata.items():
                    if field == "custom_fields" and isinstance(value, dict):
                        # Flatten custom_fields nel custom_data principale
                        for custom_field, custom_value in value.items():
                            formatted_recipient["custom_data"][custom_field] = self.format_recursive(custom_value, variables)
                    else:
                        formatted_recipient["custom_data"][field] = self.format_recursive(value, variables)
            
            # Converti custom_data in JSON string se presente (per compatibilità API)
            if "custom_data" in formatted_recipient:
                formatted_recipient["custom_data"] = json.dumps(formatted_recipient["custom_data"])
            
            logger.debug(f"Recipient {recipient_index} processato: {formatted_recipient}")
            return formatted_recipient
            
        except Exception as e:
            logger.error(f"Errore processando recipient {recipient_index}: {e}")
            self._save_error_result(variables, f"Errore processando recipient {recipient_index}: {e}")
            return None