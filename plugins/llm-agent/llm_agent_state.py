import logging
import json
from datetime import datetime
from .base_state import BaseState
from langchain.chains import ConversationChain, LLMChain 

logger = logging.getLogger(__name__)

class LLMAgentState(BaseState):
    """
    Stato LLM Agent universale che supporta multipli provider LLM tramite LangChain.
    Supporta OpenAI, Anthropic, Ollama, HuggingFace e altri provider.
    """
    state_type = "llm_agent"
    
    def __init__(self, name, state_config, global_context):
        super().__init__(name, state_config, global_context)
        self._llm = None
        self._chain = None
        self._memory = None
        
    def _get_provider_config(self):
        """Estrae la configurazione del provider LLM."""
        provider = self.state_config.get("provider", "openai").lower()
        model = self.state_config.get("model", "gpt-4.1-nano")
        temperature = float(self.state_config.get("temperature", 0.7))
        max_tokens = self.state_config.get("max_tokens", 1000)
        
        return {
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    
    def _initialize_llm(self, variables):
        """Inizializza il modello LLM basato sul provider configurato."""
        try:
            # --- MODIFICHE QUI ---
            # Importazioni aggiornate ai nuovi pacchetti specifici
            from langchain_community.llms import Ollama, HuggingFacePipeline
            from langchain_openai import OpenAI, ChatOpenAI
            from langchain_anthropic import ChatAnthropic
            # --- FINE MODIFICHE ---
        except ImportError:
            logger.error("Uno o più pacchetti LangChain (es. langchain-community, langchain-openai) non sono installati.")
            raise ImportError("LangChain e i suoi componenti specifici sono richiesti per il plugin LLM Agent")
        
        config = self._get_provider_config()
        provider = config["provider"]
        
        # Formatta le configurazioni con le variabili
        api_key = self.format_recursive(self.state_config.get("api_key"), variables)
        base_url = self.format_recursive(self.state_config.get("base_url"), variables)
        
        try:
            if provider == "openai":
                if self.state_config.get("chat_mode", True):
                    self._llm = ChatOpenAI(
                        model=config["model"],
                        temperature=config["temperature"],
                        max_tokens=config["max_tokens"],
                        openai_api_key=api_key,
                        openai_api_base=base_url
                    )
                else:
                    self._llm = OpenAI(
                        model=config["model"],
                        temperature=config["temperature"],
                        max_tokens=config["max_tokens"],
                        openai_api_key=api_key,
                        openai_api_base=base_url
                    )
                    
            elif provider == "anthropic":
                self._llm = ChatAnthropic(
                    model=config["model"],
                    temperature=config["temperature"],
                    max_tokens_to_sample=config["max_tokens"], # Nota: Anthropic usa 'max_tokens_to_sample'
                    anthropic_api_key=api_key
                )
                
            elif provider == "ollama":
                self._llm = Ollama(
                    model=config["model"],
                    temperature=config["temperature"],
                    base_url=base_url or "http://localhost:11434"
                )
                
            elif provider == "huggingface":
                # Per HuggingFace, usiamo pipeline locale
                try:
                    from transformers import pipeline
                    pipe = pipeline(
                        "text-generation",
                        model=config["model"],
                        temperature=config["temperature"],
                        max_new_tokens=config["max_tokens"]
                    )
                    self._llm = HuggingFacePipeline(pipeline=pipe)
                except ImportError:
                    logger.error("transformers non installato per HuggingFace")
                    raise
                    
            else:
                raise ValueError(f"Provider non supportato: {provider}")
                
            logger.info(f"LLM inizializzato: {provider}/{config['model']}")
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione LLM {provider}: {e}")
            raise
    
    def _initialize_memory(self):
        """Inizializza la memoria per conversazioni."""
        memory_config = self.state_config.get("memory", {})
        if not memory_config or not memory_config.get("enabled", False):
            return None
            
        try:
            # --- MODIFICHE QUI ---
            from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
            # Le classi di memoria sono ancora in langchain, ma è bene sapere che potrebbero spostarsi.
            # Per ora, questo è corretto.
            # --- FINE MODIFICHE ---
            
            memory_type = memory_config.get("type", "buffer")
            memory_key = memory_config.get("key", "chat_history")
            
            if memory_type == "buffer":
                self._memory = ConversationBufferMemory(
                    memory_key=memory_key,
                    return_messages=True
                )
            elif memory_type == "summary":
                self._memory = ConversationSummaryMemory(
                    llm=self._llm,
                    memory_key=memory_key,
                    return_messages=True
                )
            
            logger.info(f"Memoria inizializzata: {memory_type}")
            
        except ImportError:
            logger.warning("Memoria non disponibile, LangChain non completo")
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione memoria: {e}")
            
    # Il resto della classe rimane invariato...
    # ... ( _initialize_chain, _format_prompt, execute ) ...
    # Ho omesso il resto del codice per brevità, dato che non richiede modifiche.
    # Assicurati di copiare le funzioni _initialize_llm e _initialize_memory aggiornate nel tuo file.
    
    # ... Incolla qui il resto della tua classe ...
    def _initialize_chain(self):
        """Inizializza la chain LangChain."""
        chain_type = self.state_config.get("chain_type", "simple")
        
        try:
            from langchain.chains import LLMChain, ConversationChain
            from langchain.prompts import PromptTemplate
            
            if chain_type == "simple":
                system_prompt = self.state_config.get("system_prompt", "")

                
                # Per evitare problemi con LangChain, usiamo sempre {input} come placeholder
                # La formattazione complessa verrà gestita nel metodo _format_prompt
                if system_prompt:
                    template = f"{system_prompt}\n\nUser: {{input}}\nAssistant:"
                else:
                    template = "{input}"
                
                prompt = PromptTemplate(
                    template=template,
                    input_variables=["input"]
                )
                
                self._chain = LLMChain(
                    llm=self._llm,
                    prompt=prompt,
                    verbose=self.state_config.get("verbose", False)
                )
                
            elif chain_type == "conversation":
                self._chain = ConversationChain(
                    llm=self._llm,
                    memory=self._memory,
                    verbose=self.state_config.get("verbose", False)
                )
                
            else:
                logger.warning(f"Chain type '{chain_type}' non supportato, uso 'simple'")
                # Ricadi su una configurazione 'simple' di default
                self.state_config['chain_type'] = 'simple'
                self._initialize_chain()
                return

            logger.info(f"Chain inizializzata: {chain_type}")
            
        except ImportError:
            logger.error("LangChain chains non disponibili")
            raise
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione chain: {e}")
            raise

    def _format_prompt(self, variables):
        """Formatta il prompt con le variabili disponibili."""
        user_prompt_template = self.state_config.get("user_prompt", "{input}")
        # Formatta il template del prompt utente con le variabili usando il sistema migliorato
        formatted_prompt = self.format_recursive(user_prompt_template, variables)
        logger.debug(f"Prompt formattato: {formatted_prompt}")  # Debug: mostra il prompt formattato
        # Se 'input' è una chiave specifica nella configurazione, il suo valore formattato ha la priorità
        input_value = self.state_config.get("input")
        if input_value:
            return self.format_recursive(input_value, variables)

        return formatted_prompt

    def execute(self, variables):
        logger.debug(f"Esecuzione LLM Agent '{self.name}' con configurazione: {self.state_config}")
        
        try:
            if self._llm is None:
                self._initialize_llm(variables)
                self._initialize_memory()
                self._initialize_chain()
            
            formatted_input = self._format_prompt(variables)
            
            start_time = datetime.now()
            
            # NOTA: .run() e .predict() sono deprecati in favore di .invoke()
            # .invoke() accetta un dizionario e restituisce un dizionario
            if isinstance(self._chain, ConversationChain):
                # ConversationChain si aspetta 'input' nel dizionario
                response_dict = self._chain.invoke({"input": formatted_input})
                result = response_dict.get('response', '')
            else: # Per LLMChain
                response_dict = self._chain.invoke({"input": formatted_input})
                result = response_dict.get('text', '')

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"LLM Agent completato in {execution_time:.2f}s")
            
            output_data = {
                "response": result,
                "provider": self._get_provider_config()["provider"],
                "model": self._get_provider_config()["model"],
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = output_data
            
            response_key = self.state_config.get("response_key", "llm_response")
            variables[response_key] = result
            
            result_preview = result[:200] + "..." if len(result) > 200 else result
            logger.info(f"LLM Response: {result_preview}")
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except Exception as e:
            error_msg = f"❌ Errore nell'esecuzione LLM Agent: {e}"
            logger.error(error_msg, exc_info=True) # Aggiunto exc_info per un traceback completo
            
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": str(e),
                    "provider": self._get_provider_config().get("provider", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            
            return self.state_config.get("error_transition", "end")
