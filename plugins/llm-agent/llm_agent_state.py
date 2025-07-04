import logging
import json
from datetime import datetime
from .base_state import BaseState

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
        model = self.state_config.get("model", "gpt-3.5-turbo")
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
            from langchain.llms import OpenAI, Ollama
            from langchain.chat_models import ChatOpenAI, ChatAnthropic
            from langchain.llms import HuggingFacePipeline
        except ImportError:
            logger.error("LangChain non installato. Installa con: pip install langchain")
            raise ImportError("LangChain è richiesto per il plugin LLM Agent")
        
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
                    max_tokens=config["max_tokens"],
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
            from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
            
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
    
    def _initialize_chain(self):
        """Inizializza la chain LangChain."""
        chain_type = self.state_config.get("chain_type", "simple")
        
        try:
            from langchain.chains import LLMChain, ConversationChain
            from langchain.prompts import PromptTemplate, ChatPromptTemplate
            
            if chain_type == "simple":
                # Chain semplice con prompt template
                system_prompt = self.state_config.get("system_prompt", "")
                user_prompt = self.state_config.get("user_prompt", "{input}")
                
                if system_prompt:
                    template = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
                else:
                    template = user_prompt
                
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
                # Chain conversazionale con memoria
                self._chain = ConversationChain(
                    llm=self._llm,
                    memory=self._memory,
                    verbose=self.state_config.get("verbose", False)
                )
                
            else:
                # Fallback a chain semplice
                logger.warning(f"Chain type '{chain_type}' non supportato, uso 'simple'")
                self._initialize_chain_simple()
                
            logger.info(f"Chain inizializzata: {chain_type}")
            
        except ImportError:
            logger.error("LangChain chains non disponibili")
            raise
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione chain: {e}")
            raise
    
    def _format_prompt(self, variables):
        """Formatta il prompt con le variabili disponibili."""
        user_prompt = self.state_config.get("user_prompt", "{input}")
        input_text = self.state_config.get("input", "")
        
        # Se c'è un input specifico, usalo
        if input_text:
            formatted_input = self.format_recursive(input_text, variables)
        else:
            # Altrimenti cerca una variabile 'input' o usa il prompt direttamente
            formatted_input = variables.get("input", user_prompt)
        
        return self.format_recursive(formatted_input, variables)
    
    def execute(self, variables):
        logger.debug(f"Esecuzione LLM Agent '{self.name}' con configurazione: {self.state_config}")
        
        try:
            # Inizializza componenti se non già fatto
            if self._llm is None:
                self._initialize_llm(variables)
                self._initialize_memory()
                self._initialize_chain()
            
            # Prepara l'input
            formatted_input = self._format_prompt(variables)
            
            # Esegui la chain
            start_time = datetime.now()
            
            if self.state_config.get("chain_type", "simple") == "conversation":
                result = self._chain.predict(input=formatted_input)
            else:
                result = self._chain.run(input=formatted_input)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"LLM Agent completato in {execution_time:.2f}s")
            
            # Prepara l'output
            output_data = {
                "response": result,
                "provider": self._get_provider_config()["provider"],
                "model": self._get_provider_config()["model"],
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Salva l'output se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = output_data
            
            # Salva anche solo la risposta se specificato
            response_key = self.state_config.get("response_key", "llm_response")
            variables[response_key] = result
            
            # Log del risultato (troncato se troppo lungo)
            result_preview = result[:200] + "..." if len(result) > 200 else result
            logger.info(f"LLM Response: {result_preview}")
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except Exception as e:
            error_msg = f"Errore nell'esecuzione LLM Agent: {e}"
            logger.error(error_msg)
            
            # Salva l'errore nell'output se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": str(e),
                    "provider": self._get_provider_config()["provider"],
                    "timestamp": datetime.now().isoformat()
                }
            
            return self.state_config.get("error_transition", "end")
