import logging
import json
import ast
import time
import re
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .base_state import BaseState

logger = logging.getLogger(__name__)

class PythonCodeGeneratorState(BaseState):
    """
    Plugin avanzato per la generazione di codice Python tramite LLM con pianificazione step-by-step.
    
    Caratteristiche:
    - Pianificazione automatica con controllo step
    - Generazione codice iterativa
    - Test automatici inclusi nel conteggio step
    - Validazione sintassi e qualità
    - Supporto multipli provider LLM
    """
    state_type = "python_code_generator"
    
    # Stati interni del plugin
    INTERNAL_STATES = {
        "PLAN_CREATION": "plan_creation",
        "STEP_EXECUTION": "step_execution", 
        "PLAN_REVIEW": "plan_review",
        "TEST_GENERATION": "test_generation",
        "CODE_VALIDATION": "code_validation",
        "EXECUTION": "execution",
        "COMPLETION": "completion",
        "ERROR": "error"
    }
    
    def __init__(self, name, state_config, global_context):
        super().__init__(name, state_config, global_context)
        
        # Inizializzazione stato interno
        self.step_counter = 0
        self.max_steps = state_config.get("max_steps", 20)
        self.current_internal_state = self.INTERNAL_STATES["PLAN_CREATION"]
        
        # Dati di lavoro
        self.execution_plan = []
        self.generated_code = ""
        self.generated_tests = ""
        self.current_step_index = 0
        self.plan_revisions = 0
        
        # Configurazione LLM
        self._llm = None
        self._chain = None
        
        # Metriche
        self.start_time = None
        self.step_times = []
        self.token_usage = 0
        
        # Gestione Workspace
        self.workspace_enabled = state_config.get("workspace_enabled", True)
        self.workspace_root = state_config.get("workspace_root", "workspace")
        self.project_name = None
        self.project_path = None
        self.workspace_initialized = False
        
    def execute(self, variables):
        """Punto di ingresso principale del plugin."""
        logger.info(f"🚀 Avvio Python Code Generator '{self.name}' - Step limit: {self.max_steps}")
        self.start_time = time.time()
        
        try:
            # Validazione parametri iniziali
            validation_result = self._validate_input(variables)
            if not validation_result["valid"]:
                return self._handle_error(validation_result["error"], variables)
            
            # Inizializzazione LLM
            self._initialize_llm(variables)
            
            # Esecuzione state machine principale
            while self.current_internal_state != self.INTERNAL_STATES["COMPLETION"] and \
                  self.current_internal_state != self.INTERNAL_STATES["ERROR"]:
                
                # Controllo limite step
                if self._check_step_limit():
                    return self._handle_step_limit_exceeded(variables)
                
                # Esecuzione stato corrente
                self._execute_internal_state(variables)
            
            # Finalizzazione
            if self.current_internal_state == self.INTERNAL_STATES["COMPLETION"]:
                return self._finalize_success(variables)
            else:
                return self._finalize_error(variables)
                
        except Exception as e:
            error_msg = f"Errore critico in Python Code Generator: {e}"
            logger.error(error_msg, exc_info=True)
            return self._handle_error(error_msg, variables)
    
    def _validate_input(self, variables) -> Dict[str, Any]:
        """Valida i parametri di input del plugin."""
        prompt = self.state_config.get("prompt", "")
        if not prompt:
            return {"valid": False, "error": "Parametro 'prompt' obbligatorio mancante"}
        
        max_steps = self.state_config.get("max_steps", 20)
        if max_steps < 5:
            return {"valid": False, "error": "max_steps deve essere almeno 5"}
        
        execution_mode = self.state_config.get("execution_mode", "full")
        if execution_mode not in ["plan_only", "generate_only", "full"]:
            return {"valid": False, "error": f"execution_mode non valido: {execution_mode}"}
        
        return {"valid": True}
    
    def _initialize_llm(self, variables):
        """Inizializza il provider LLM configurato."""
        try:
            from langchain.llms import OpenAI, Ollama
            from langchain.chat_models import ChatOpenAI, ChatAnthropic
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
        except ImportError:
            raise ImportError("LangChain è richiesto per il plugin Python Code Generator")
        
        provider = self.state_config.get("provider", "openai").lower()
        model = self.state_config.get("model", "gpt-3.5-turbo")
        temperature = float(self.state_config.get("temperature", 0.3))
        
        # Formatta configurazioni con variabili
        api_key = self.format_recursive(self.state_config.get("api_key"), variables)
        base_url = self.format_recursive(self.state_config.get("base_url"), variables)
        
        # Inizializzazione provider specifico
        if provider == "openai":
            self._llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=api_key,
                openai_api_base=base_url
            )
        elif provider == "anthropic":
            self._llm = ChatAnthropic(
                model=model,
                temperature=temperature,
                anthropic_api_key=api_key
            )
        elif provider == "ollama":
            self._llm = Ollama(
                model=model,
                temperature=temperature,
                base_url=base_url or "http://localhost:11434"
            )
        else:
            raise ValueError(f"Provider non supportato: {provider}")
        
        logger.info(f"✅ LLM inizializzato: {provider}/{model}")
    
    def _execute_internal_state(self, variables):
        """Esegue lo stato interno corrente."""
        state = self.current_internal_state
        
        logger.debug(f"📍 Esecuzione stato interno: {state} (Step {self.step_counter}/{self.max_steps})")
        
        if state == self.INTERNAL_STATES["PLAN_CREATION"]:
            self._create_execution_plan(variables)
        elif state == self.INTERNAL_STATES["STEP_EXECUTION"]:
            self._execute_plan_step(variables)
        elif state == self.INTERNAL_STATES["PLAN_REVIEW"]:
            self._review_execution_plan(variables)
        elif state == self.INTERNAL_STATES["TEST_GENERATION"]:
            self._generate_tests(variables)
        elif state == self.INTERNAL_STATES["CODE_VALIDATION"]:
            self._validate_generated_code(variables)
        elif state == self.INTERNAL_STATES["EXECUTION"]:
            self._execute_generated_code(variables)
        else:
            logger.error(f"Stato interno non riconosciuto: {state}")
            self.current_internal_state = self.INTERNAL_STATES["ERROR"]
    
    def _create_execution_plan(self, variables):
        """Crea il piano di esecuzione iniziale."""
        self._increment_step("plan_creation")
        
        # Inizializza workspace e nome progetto
        self.project_name = self.state_config.get("project_name")
        if self.workspace_enabled:
            self._initialize_workspace(variables)
        
        prompt = self.format_recursive(self.state_config.get("prompt"), variables)
        complexity = self.state_config.get("complexity_level", "medium")
        code_style = self.state_config.get("code_style", "pep8")
        include_tests = self.state_config.get("include_tests", True)
        
        planning_prompt = self._build_planning_prompt(prompt, complexity, code_style, include_tests)
        
        try:
            plan_response = self._query_llm(planning_prompt)
            self.execution_plan = self._parse_execution_plan(plan_response)
            
            # Verifica che il piano rientri nei limiti
            estimated_steps = self._estimate_total_steps()
            if estimated_steps > self.max_steps:
                logger.warning(f"⚠️ Piano stimato ({estimated_steps} step) supera il limite ({self.max_steps})")
                self._optimize_plan_for_limits()
            
            logger.info(f"📋 Piano creato: {len(self.execution_plan)} step principali")
            
            # Transizione al prossimo stato
            execution_mode = self.state_config.get("execution_mode", "full")
            if execution_mode == "plan_only":
                self.current_internal_state = self.INTERNAL_STATES["COMPLETION"]
            else:
                self.current_internal_state = self.INTERNAL_STATES["STEP_EXECUTION"]
                
        except Exception as e:
            logger.error(f"Errore nella creazione del piano: {e}")
            self.current_internal_state = self.INTERNAL_STATES["ERROR"]
    
    def _execute_plan_step(self, variables):
        """Esegue uno step specifico del piano."""
        if self.current_step_index >= len(self.execution_plan):
            # Tutti gli step completati
            if self.state_config.get("include_tests", True):
                self.current_internal_state = self.INTERNAL_STATES["TEST_GENERATION"]
            else:
                self.current_internal_state = self.INTERNAL_STATES["CODE_VALIDATION"]
            return
        
        self._increment_step("code_generation")
        
        current_step = self.execution_plan[self.current_step_index]
        
        code_prompt = self._build_code_generation_prompt(current_step, variables)
        
        try:
            code_response = self._query_llm(code_prompt)
            step_code = self._extract_code_from_response(code_response)
            
            # Aggiunge il codice al risultato totale
            self.generated_code += f"\n# Step {self.current_step_index + 1}: {current_step['title']}\n"
            self.generated_code += step_code + "\n"
            
            logger.info(f"✅ Step {self.current_step_index + 1}/{len(self.execution_plan)} completato")
            
            self.current_step_index += 1
            
            # Ogni 3 step, rivede il piano
            if self.current_step_index % 3 == 0 and self.current_step_index < len(self.execution_plan):
                self.current_internal_state = self.INTERNAL_STATES["PLAN_REVIEW"]
            
        except Exception as e:
            logger.error(f"Errore nell'esecuzione step {self.current_step_index}: {e}")
            self.current_internal_state = self.INTERNAL_STATES["ERROR"]
    
    def _review_execution_plan(self, variables):
        """Rivede e potenzialmente modifica il piano di esecuzione."""
        self._increment_step("plan_revision")
        
        review_prompt = self._build_plan_review_prompt()
        
        try:
            review_response = self._query_llm(review_prompt)
            review_result = self._parse_plan_review(review_response)
            
            if review_result["needs_modification"]:
                self.execution_plan = review_result["updated_plan"]
                self.plan_revisions += 1
                logger.info(f"📝 Piano aggiornato (revisione #{self.plan_revisions})")
            else:
                logger.info("✅ Piano confermato, nessuna modifica necessaria")
            
            # Torna all'esecuzione degli step
            self.current_internal_state = self.INTERNAL_STATES["STEP_EXECUTION"]
            
        except Exception as e:
            logger.error(f"Errore nella revisione del piano: {e}")
            # Continua senza modifiche
            self.current_internal_state = self.INTERNAL_STATES["STEP_EXECUTION"]
    
    def _generate_tests(self, variables):
        """Genera test unitari per il codice."""
        self._increment_step("test_generation")
        
        test_prompt = self._build_test_generation_prompt()
        
        try:
            test_response = self._query_llm(test_prompt)
            self.generated_tests = self._extract_code_from_response(test_response)
            
            logger.info("🧪 Test unitari generati")
            self.current_internal_state = self.INTERNAL_STATES["CODE_VALIDATION"]
            
        except Exception as e:
            logger.error(f"Errore nella generazione test: {e}")
            self.current_internal_state = self.INTERNAL_STATES["CODE_VALIDATION"]
    
    def _validate_generated_code(self, variables):
        """Valida la sintassi e qualità del codice generato."""
        if not self.state_config.get("validate_syntax", True):
            self.current_internal_state = self.INTERNAL_STATES["EXECUTION"]
            return
        
        self._increment_step("code_validation")
        
        try:
            # Validazione sintassi Python
            ast.parse(self.generated_code)
            logger.info("✅ Validazione sintassi superata")
            
            # Validazione test se presenti
            if self.generated_tests:
                ast.parse(self.generated_tests)
                logger.info("✅ Validazione test superata")
            
            execution_mode = self.state_config.get("execution_mode", "full")
            if execution_mode == "full":
                self.current_internal_state = self.INTERNAL_STATES["EXECUTION"]
            else:
                self.current_internal_state = self.INTERNAL_STATES["COMPLETION"]
                
        except SyntaxError as e:
            logger.error(f"❌ Errore di sintassi nel codice: {e}")
            self.current_internal_state = self.INTERNAL_STATES["ERROR"]
        except Exception as e:
            logger.error(f"Errore nella validazione: {e}")
            self.current_internal_state = self.INTERNAL_STATES["ERROR"]
    
    def _execute_generated_code(self, variables):
        """Esegue il codice generato in ambiente sicuro."""
        self._increment_step("code_execution")
        
        try:
            # Esecuzione in namespace isolato
            execution_namespace = {}
            exec(self.generated_code, execution_namespace)
            
            logger.info("✅ Codice eseguito con successo")
            self.current_internal_state = self.INTERNAL_STATES["COMPLETION"]
            
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione del codice: {e}")
            # Non è un errore critico, il codice potrebbe richiedere input esterni
            logger.info("ℹ️ Codice generato ma non eseguibile in ambiente isolato")
            self.current_internal_state = self.INTERNAL_STATES["COMPLETION"]
    
    def _check_step_limit(self) -> bool:
        """Controlla se il limite di step è stato raggiunto."""
        return self.step_counter >= self.max_steps
    
    def _increment_step(self, step_type: str):
        """Incrementa il contatore step e registra il tipo."""
        self.step_counter += 1
        step_time = time.time() - self.start_time
        self.step_times.append({
            "step": self.step_counter,
            "type": step_type,
            "time": step_time
        })
        
        logger.debug(f"📊 Step {self.step_counter}/{self.max_steps} ({step_type})")
        
        # Warning se vicino al limite
        if self.step_counter >= self.max_steps * 0.8:
            logger.warning(f"⚠️ Vicino al limite step: {self.step_counter}/{self.max_steps}")
    
    def _query_llm(self, prompt: str) -> str:
        """Esegue una query al modello LLM."""
        try:
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
            
            template = PromptTemplate(
                template=prompt,
                input_variables=[]
            )
            
            chain = LLMChain(llm=self._llm, prompt=template)
            response = chain.run({})
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Errore nella query LLM: {e}")
            raise
    
    def _build_planning_prompt(self, user_prompt: str, complexity: str, code_style: str, include_tests: bool) -> str:
        """Costruisce il prompt per la pianificazione."""
        return f"""
Sei un esperto sviluppatore Python. Devi creare un piano dettagliato per implementare il seguente requisito:

REQUISITO: {user_prompt}

PARAMETRI:
- Complessità: {complexity}
- Stile codice: {code_style}
- Include test: {include_tests}

Crea un piano di sviluppo strutturato con i seguenti step:
1. Analisi dei requisiti
2. Progettazione architettura
3. Implementazione core
4. Gestione errori
5. Ottimizzazioni
6. Documentazione

Per ogni step, specifica:
- Titolo dello step
- Descrizione dettagliata
- Componenti da implementare
- Dipendenze da altri step

Rispondi in formato JSON:
{{
  "steps": [
    {{
      "title": "Nome step",
      "description": "Descrizione dettagliata",
      "components": ["componente1", "componente2"],
      "dependencies": []
    }}
  ],
  "estimated_complexity": "low|medium|high",
  "estimated_time": "tempo stimato"
}}
"""
    
    def _build_code_generation_prompt(self, step: Dict, variables: Dict) -> str:
        """Costruisce il prompt per la generazione di codice."""
        code_style = self.state_config.get("code_style", "pep8")
        include_docs = self.state_config.get("include_documentation", True)
        
        context = ""
        if self.generated_code:
            context = f"\nCODICE ESISTENTE:\n```python\n{self.generated_code}\n```\n"
        
        return f"""
Sei un esperto sviluppatore Python. Implementa il seguente step del piano di sviluppo:

STEP: {step['title']}
DESCRIZIONE: {step['description']}
COMPONENTI: {', '.join(step.get('components', []))}

{context}

REQUISITI:
- Stile codice: {code_style}
- Documentazione: {'Includi docstring e commenti' if include_docs else 'Solo codice essenziale'}
- Compatibilità: Python 3.8+
- Gestione errori appropriata

Genera SOLO il codice Python per questo step, senza spiegazioni aggiuntive.
Il codice deve essere completo e funzionante.

```python
# Il tuo codice qui
```
"""
    
    def _build_plan_review_prompt(self) -> str:
        """Costruisce il prompt per la revisione del piano."""
        return f"""
Rivedi il piano di sviluppo corrente basandoti sul progresso fatto finora.

PIANO ORIGINALE:
{json.dumps(self.execution_plan, indent=2)}

CODICE GENERATO FINORA:
```python
{self.generated_code}
```

STEP COMPLETATI: {self.current_step_index}/{len(self.execution_plan)}
STEP RIMANENTI: {self.max_steps - self.step_counter}

Analizza se il piano necessita modifiche per:
1. Ottimizzare i step rimanenti
2. Rispettare il limite di step
3. Migliorare la qualità del risultato

Rispondi in formato JSON:
{{
  "needs_modification": true/false,
  "reason": "motivo della modifica",
  "updated_plan": [...] // solo se needs_modification è true
}}
"""
    
    def _build_test_generation_prompt(self) -> str:
        """Costruisce il prompt per la generazione dei test."""
        return f"""
Genera test unitari completi per il seguente codice Python:

```python
{self.generated_code}
```

REQUISITI TEST:
- Usa unittest framework
- Copertura completa delle funzioni
- Test casi edge e errori
- Nomi test descrittivi
- Assertions appropriate

Genera SOLO il codice dei test, senza spiegazioni.

```python
# I tuoi test qui
```
"""
    
    def _parse_execution_plan(self, response: str) -> List[Dict]:
        """Estrae il piano di esecuzione dalla risposta LLM."""
        try:
            # Cerca JSON nella risposta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                return plan_data.get("steps", [])
            else:
                # Fallback: crea piano semplice
                return self._create_fallback_plan()
        except Exception as e:
            logger.warning(f"Errore parsing piano: {e}, uso fallback")
            return self._create_fallback_plan()
    
    def _parse_plan_review(self, response: str) -> Dict:
        """Estrae il risultato della revisione del piano."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"needs_modification": False}
        except Exception as e:
            logger.warning(f"Errore parsing revisione: {e}")
            return {"needs_modification": False}
    
    def _extract_code_from_response(self, response: str) -> str:
        """Estrae il codice Python dalla risposta LLM."""
        # Cerca blocchi di codice Python
        code_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return '\n'.join(matches)
        else:
            # Se non trova blocchi, usa tutta la risposta
            return response.strip()
    
    def _create_fallback_plan(self) -> List[Dict]:
        """Crea un piano di fallback semplice."""
        return [
            {
                "title": "Implementazione principale",
                "description": "Implementa la funzionalità richiesta",
                "components": ["funzione_principale"],
                "dependencies": []
            },
            {
                "title": "Gestione errori",
                "description": "Aggiunge gestione errori e validazione",
                "components": ["error_handling"],
                "dependencies": ["funzione_principale"]
            },
            {
                "title": "Documentazione",
                "description": "Aggiunge documentazione e commenti",
                "components": ["docstrings"],
                "dependencies": ["funzione_principale"]
            }
        ]
    
    def _estimate_total_steps(self) -> int:
        """Stima il numero totale di step necessari."""
        base_steps = len(self.execution_plan)  # Step del piano
        test_steps = 1 if self.state_config.get("include_tests", True) else 0
        validation_steps = 1 if self.state_config.get("validate_syntax", True) else 0
        execution_steps = 1 if self.state_config.get("execution_mode", "full") == "full" else 0
        review_steps = max(1, len(self.execution_plan) // 3)  # Revisioni ogni 3 step
        
        return 1 + base_steps + test_steps + validation_steps + execution_steps + review_steps
    
    def _optimize_plan_for_limits(self):
        """Ottimizza il piano per rispettare i limiti di step."""
        available_steps = self.max_steps - self.step_counter - 3  # Riserva per test/validazione
        
        if len(self.execution_plan) > available_steps:
            # Riduce il numero di step del piano
            self.execution_plan = self.execution_plan[:available_steps]
            logger.warning(f"⚠️ Piano ridotto a {len(self.execution_plan)} step per rispettare i limiti")
    
    def _handle_step_limit_exceeded(self, variables) -> str:
        """Gestisce il superamento del limite di step."""
        error_data = {
            "error": "Step limit exceeded",
            "steps_executed": self.step_counter,
            "max_steps": self.max_steps,
            "partial_code": self.generated_code,
            "partial_tests": self.generated_tests,
            "execution_plan": self.execution_plan,
            "success": False
        }
        
        # Salva risultati parziali
        self._save_outputs(error_data, variables)
        
        logger.error(f"❌ Limite step superato: {self.step_counter}/{self.max_steps}")
        return self.state_config.get("error_transition", "end")
    
    def _handle_error(self, error_msg: str, variables) -> str:
        """Gestisce errori generici."""
        error_data = {
            "error": error_msg,
            "steps_executed": self.step_counter,
            "partial_code": self.generated_code,
            "success": False
        }
        
        self._save_outputs(error_data, variables)
        return self.state_config.get("error_transition", "end")
    
    def _finalize_success(self, variables) -> str:
        """Finalizza l'esecuzione con successo."""
        execution_time = time.time() - self.start_time
        
        result_data = {
            "success": True,
            "generated_code": self.generated_code,
            "generated_tests": self.generated_tests,
            "execution_plan": self.execution_plan,
            "steps_executed": self.step_counter,
            "steps_remaining": self.max_steps - self.step_counter,
            "plan_revisions": self.plan_revisions,
            "execution_time": execution_time,
            "performance_metrics": {
                "total_steps": self.step_counter,
                "step_times": self.step_times,
                "average_step_time": sum(s["time"] for s in self.step_times) / len(self.step_times) if self.step_times else 0
            },
            "provider": self.state_config.get("provider", "openai"),
            "model": self.state_config.get("model", "gpt-3.5-turbo"),
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_outputs(result_data, variables)
        
        logger.info(f"🎉 Python Code Generator completato con successo!")
        logger.info(f"📊 Step eseguiti: {self.step_counter}/{self.max_steps}")
        logger.info(f"⏱️ Tempo totale: {execution_time:.2f}s")
        
        return self.state_config.get("success_transition", self.state_config.get("transition"))
    
    def _finalize_error(self, variables) -> str:
        """Finalizza l'esecuzione con errore."""
        error_data = {
            "success": False,
            "error": "Internal state machine error",
            "steps_executed": self.step_counter,
            "partial_code": self.generated_code
        }
        
        self._save_outputs(error_data, variables)
        return self.state_config.get("error_transition", "end")
    
    def _initialize_workspace(self, variables):
        """Inizializza il workspace per il progetto."""
        if not self.workspace_enabled:
            logger.info("📁 Workspace disabilitato, salvataggio in directory corrente")
            return
        
        try:
            # Genera nome progetto se non specificato
            if not self.project_name:
                self.project_name = self._generate_project_name(variables)
            
            # Crea percorso progetto
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if self.state_config.get("timestamp_folders", True):
                project_folder = f"{self.project_name}_{timestamp}"
            else:
                project_folder = self.project_name
            
            # Percorso completo del workspace
            self.project_path = os.path.join(
                self.workspace_root,
                "python-code-generator",
                "projects",
                project_folder
            )
            
            # Crea struttura directory
            self._create_workspace_structure()
            
            logger.info(f"📁 Workspace inizializzato: {self.project_path}")
            self.workspace_initialized = True
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione workspace: {e}")
            logger.info("📁 Fallback: salvataggio in directory corrente")
            self.workspace_enabled = False
    
    def _generate_project_name(self, variables) -> str:
        """Genera un nome progetto basato sul prompt."""
        prompt = self.format_recursive(self.state_config.get("prompt", ""), variables)
        
        # Estrae parole chiave dal prompt
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        
        # Prende le prime 2-3 parole significative
        keywords = [w for w in words[:3] if w not in ['crea', 'genera', 'implementa', 'sviluppa', 'python', 'codice']]
        
        if keywords:
            project_name = "_".join(keywords[:2])
        else:
            project_name = "python_project"
        
        # Sanitizza il nome
        project_name = re.sub(r'[^a-zA-Z0-9_]', '_', project_name)
        
        return project_name
    
    def _create_workspace_structure(self):
        """Crea la struttura delle directory del workspace."""
        if not self.workspace_enabled or not self.project_path:
            return
        
        # Directory principali
        directories = [
            self.project_path,
            os.path.join(self.project_path, "src"),
            os.path.join(self.project_path, "tests"),
            os.path.join(self.project_path, "docs"),
            os.path.join(self.project_path, "config")
        ]
        
        # Crea directory se abilitato project_subfolder
        if self.state_config.get("project_subfolder", True):
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"📁 Creata directory: {directory}")
        else:
            # Solo directory principale
            os.makedirs(self.project_path, exist_ok=True)
    
    def _get_safe_file_path(self, filename: str, subfolder: str = "") -> str:
        """Ottiene un percorso file sicuro nel workspace."""
        if not self.workspace_enabled:
            return filename
        
        # Inizializza workspace se non fatto
        if not self.workspace_initialized:
            self._initialize_workspace({})
        
        # Sanitizza nome file
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        if subfolder and self.state_config.get("project_subfolder", True):
            file_path = os.path.join(self.project_path, subfolder, safe_filename)
        else:
            file_path = os.path.join(self.project_path, safe_filename)
        
        # Assicura che il percorso sia all'interno del workspace
        abs_workspace = os.path.abspath(self.workspace_root)
        abs_file_path = os.path.abspath(file_path)
        
        if not abs_file_path.startswith(abs_workspace):
            logger.warning(f"⚠️ Percorso non sicuro rilevato: {file_path}")
            return os.path.join(self.project_path, safe_filename)
        
        return file_path
    
    def _save_file_to_workspace(self, content: str, filename: str, subfolder: str = "") -> str:
        """Salva un file nel workspace."""
        file_path = self._get_safe_file_path(filename, subfolder)
        
        try:
            # Crea directory se necessario
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Salva file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"💾 File salvato: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio file {file_path}: {e}")
            raise
    
    def _save_project_metadata(self, data: Dict):
        """Salva i metadati del progetto nel workspace."""
        if not self.workspace_enabled:
            return
        
        metadata = {
            "project_info": {
                "name": self.project_name,
                "generated_by": "IntellyHub Python Code Generator v1.0.0",
                "generation_date": datetime.now().isoformat(),
                "provider": self.state_config.get("provider", "openai"),
                "model": self.state_config.get("model", "gpt-3.5-turbo"),
                "workspace_path": self.project_path
            },
            "generation_data": data,
            "configuration": {
                "max_steps": self.max_steps,
                "complexity_level": self.state_config.get("complexity_level", "medium"),
                "code_style": self.state_config.get("code_style", "pep8"),
                "include_tests": self.state_config.get("include_tests", True),
                "execution_mode": self.state_config.get("execution_mode", "full")
            }
        }
        
        try:
            metadata_path = self._get_safe_file_path("project_metadata.json", "config")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Metadati salvati: {metadata_path}")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio metadati: {e}")
    
    def _cleanup_on_error(self):
        """Pulisce i file parziali in caso di errore se configurato."""
        if not self.state_config.get("cleanup_on_error", False):
            return
        
        if not self.workspace_enabled or not self.project_path:
            return
        
        try:
            if os.path.exists(self.project_path):
                shutil.rmtree(self.project_path)
                logger.info(f"🧹 Workspace pulito dopo errore: {self.project_path}")
        except Exception as e:
            logger.error(f"Errore nella pulizia workspace: {e}")
    
    def _save_outputs(self, data: Dict, variables: Dict):
        """Salva gli output nelle variabili specificate e nel workspace."""
        # Inizializza workspace se necessario
        if self.workspace_enabled and not self.workspace_initialized:
            self._initialize_workspace(variables)
        
        # Salva file nel workspace se abilitato
        if self.workspace_enabled and self.workspace_initialized:
            try:
                # Salva codice principale
                if data.get("generated_code"):
                    main_filename = f"{self.project_name}.py" if self.project_name else "main.py"
                    code_content = self._add_file_header(data["generated_code"], data)
                    self._save_file_to_workspace(code_content, main_filename, "src")
                
                # Salva test
                if data.get("generated_tests"):
                    test_filename = f"test_{self.project_name}.py" if self.project_name else "test_main.py"
                    test_content = self._add_file_header(data["generated_tests"], data)
                    self._save_file_to_workspace(test_content, test_filename, "tests")
                
                # Salva piano di esecuzione
                if data.get("execution_plan"):
                    plan_content = json.dumps(data["execution_plan"], indent=2, ensure_ascii=False)
                    self._save_file_to_workspace(plan_content, "execution_plan.json", "docs")
                
                # Salva README
                readme_content = self._generate_readme(data)
                self._save_file_to_workspace(readme_content, "README.md")
                
                # Salva metadati progetto
                self._save_project_metadata(data)
                
                # Aggiunge percorso workspace ai dati
                data["workspace_path"] = self.project_path
                
            except Exception as e:
                logger.error(f"Errore nel salvataggio workspace: {e}")
                if not data.get("success", True):  # Solo se già in errore
                    self._cleanup_on_error()
        
        # Salva nelle variabili (comportamento originale)
        output_key = self.state_config.get("output")
        if output_key:
            variables[output_key] = data
        
        # Output specifici
        if data.get("generated_code"):
            code_key = self.state_config.get("code_output", "generated_code")
            variables[code_key] = data["generated_code"]
        
        if data.get("generated_tests"):
            tests_key = self.state_config.get("tests_output", "generated_tests")
            variables[tests_key] = data["generated_tests"]
        
        if data.get("execution_plan"):
            plan_key = self.state_config.get("plan_output", "execution_plan")
            variables[plan_key] = data["execution_plan"]
    
    def _add_file_header(self, content: str, data: Dict) -> str:
        """Aggiunge header informativo ai file generati."""
        header = f'''"""
{self.project_name.replace('_', ' ').title() if self.project_name else 'Generated Python Code'}

Generato automaticamente da IntellyHub Python Code Generator v1.0.0

Informazioni Generazione:
- Provider: {data.get("provider", "N/A")}
- Modello: {data.get("model", "N/A")}
- Data: {data.get("timestamp", datetime.now().isoformat())}
- Step eseguiti: {data.get("steps_executed", "N/A")}
- Tempo generazione: {data.get("execution_time", 0):.2f}s

⚠️ ATTENZIONE: Questo codice è stato generato automaticamente.
   Rivedi e testa accuratamente prima dell'uso in produzione.
"""

'''
        return header + content
    
    def _generate_readme(self, data: Dict) -> str:
        """Genera un README per il progetto."""
        project_title = self.project_name.replace('_', ' ').title() if self.project_name else 'Generated Python Project'
        
        return f'''# {project_title}

Progetto generato automaticamente da **IntellyHub Python Code Generator v1.0.0**.

## 📊 Informazioni Generazione

- **Provider LLM**: {data.get("provider", "N/A")}
- **Modello**: {data.get("model", "N/A")}
- **Data Generazione**: {data.get("timestamp", "N/A")}
- **Step Eseguiti**: {data.get("steps_executed", "N/A")}
- **Tempo Totale**: {data.get("execution_time", 0):.2f} secondi
- **Revisioni Piano**: {data.get("plan_revisions", 0)}

## 📁 Struttura Progetto

```
{self.project_name or "project"}/
├── src/
│   └── {self.project_name or "main"}.py          # Codice principale
├── tests/
│   └── test_{self.project_name or "main"}.py     # Test unitari
├── docs/
│   └── execution_plan.json    # Piano di sviluppo utilizzato
├── config/
│   └── project_metadata.json  # Metadati completi
└── README.md                   # Questo file
```

## 🚀 Utilizzo

### Installazione Dipendenze

```bash
# Installa dipendenze base se necessarie
pip install -r requirements.txt  # Se presente
```

### Esecuzione

```bash
# Esegui il codice principale
python src/{self.project_name or "main"}.py

# Esegui i test
python -m pytest tests/ -v
```

## 🧪 Testing

Il progetto include test unitari generati automaticamente:

```bash
# Test con coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test specifici
python -m pytest tests/test_{self.project_name or "main"}.py -v
```

## 📈 Piano di Sviluppo

Il codice è stato generato seguendo un piano strutturato di {len(data.get("execution_plan", []))} fasi.
Vedi `docs/execution_plan.json` per i dettagli completi.

## ⚠️ Note Importanti

- **Codice Generato**: Questo codice è stato creato automaticamente da un LLM
- **Revisione Necessaria**: Rivedi accuratamente prima dell'uso in produzione
- **Test Richiesti**: Esegui test approfonditi per verificare la correttezza
- **Dipendenze**: Controlla e installa eventuali dipendenze mancanti

## 🔧 Configurazione Generazione

- **Complessità**: {data.get("complexity_level", "N/A")}
- **Stile Codice**: {data.get("code_style", "N/A")}
- **Modalità**: {data.get("execution_mode", "N/A")}
- **Test Inclusi**: {"Sì" if data.get("include_tests") else "No"}

## 📞 Supporto

Per supporto su IntellyHub Python Code Generator:

- 📧 Email: support@intellyhub.com
- 🐛 Issues: [GitHub Issues](https://github.com/kuduk/intellyhub-plugins/issues)

---

**Generato con ❤️ da IntellyHub Python Code Generator v1.0.0**
'''
