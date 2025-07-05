# 🐍 Python Code Generator Plugin v1.0.0

Plugin avanzato per IntellyHub che genera codice Python tramite LLM con pianificazione step-by-step, controllo limiti e generazione test automatica.

## 🚀 Caratteristiche Principali

- **Pianificazione Intelligente**: Crea automaticamente un piano di sviluppo strutturato
- **Controllo Step**: Limite configurabile per prevenire esecuzioni infinite
- **Generazione Iterativa**: Sviluppo del codice step-by-step con revisioni
- **Test Automatici**: Generazione di test unitari inclusa nel conteggio step
- **Multi-Provider**: Supporto OpenAI, Anthropic, Ollama
- **Validazione Sintassi**: Controllo automatico della correttezza del codice
- **Metriche Dettagliate**: Tracking completo dell'esecuzione
- **🆕 Workspace Management**: Organizzazione automatica dei file in strutture di progetto

## 📋 Requisiti

### Dipendenze Obbligatorie
```bash
pip install langchain>=0.1.0 openai>=1.0.0 anthropic>=0.8.0
```

### Dipendenze Opzionali
```bash
pip install black>=23.0.0 pylint>=2.15.0 pytest>=7.0.0
```

## 🛠️ Installazione

### Metodo 1: Package Manager (Raccomandato)

1. Aggiungi al file `plugins.yaml`:
```yaml
dependencies:
  - python-code-generator>=1.0.0
```

2. Installa:
```bash
python -m package_manager install
```

### Metodo 2: Installazione Manuale

1. Copia i file del plugin in `flow/states/`
2. Riavvia l'applicazione
3. Verifica nei log: `✅ Stato 'python_code_generator' registrato`

## 📖 Configurazione

### Parametri Base

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `prompt` | string | **obbligatorio** | Descrizione del codice da generare |
| `max_steps` | integer | 20 | Limite massimo di step |
| `provider` | string | "openai" | Provider LLM (openai/anthropic/ollama) |
| `model` | string | "gpt-3.5-turbo" | Modello specifico |
| `api_key` | string | - | Chiave API per provider cloud |

### Parametri Avanzati

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `execution_mode` | string | "full" | Modalità: plan_only/generate_only/full |
| `complexity_level` | string | "medium" | Livello: simple/medium/complex/expert |
| `code_style` | string | "pep8" | Stile: pep8/google/numpy/custom |
| `include_tests` | boolean | true | Genera test automaticamente |
| `include_documentation` | boolean | true | Includi docstring e commenti |
| `validate_syntax` | boolean | true | Valida sintassi del codice |
| `temperature` | float | 0.3 | Temperatura LLM (0.0-1.0) |

### Parametri Output

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `output` | string | - | Variabile per output completo |
| `code_output` | string | "generated_code" | Variabile per codice generato |
| `tests_output` | string | "generated_tests" | Variabile per test generati |
| `plan_output` | string | "execution_plan" | Variabile per piano esecuzione |

### 🆕 Parametri Workspace

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `workspace_enabled` | boolean | true | Abilita gestione workspace |
| `workspace_root` | string | "workspace" | Directory radice del workspace |
| `project_name` | string | auto-generato | Nome del progetto |
| `timestamp_folders` | boolean | true | Aggiunge timestamp ai nomi cartelle |
| `project_subfolder` | boolean | true | Crea sottocartelle strutturate |
| `cleanup_on_error` | boolean | false | Elimina file parziali in caso di errore |

## 🎯 Esempi di Utilizzo

### Esempio 1: Generazione Fibonacci Semplice

```yaml
variables:
  openai_api_key: "your-api-key"

states:
  generate_fibonacci:
    state_type: "python_code_generator"
    prompt: "Crea una funzione per calcolare la sequenza di Fibonacci fino a n termini"
    max_steps: 10
    provider: "openai"
    model: "gpt-3.5-turbo"
    api_key: "{openai_api_key}"
    complexity_level: "simple"
    include_tests: true
    output: "fibonacci_result"
    success_transition: "show_result"
    error_transition: "handle_error"

  show_result:
    state_type: "command"
    action:
      eval: "print(f'✅ Codice generato:\\n{fibonacci_result.generated_code}')"
    transition: "end"

  handle_error:
    state_type: "command"
    action:
      eval: "print(f'❌ Errore: {fibonacci_result.error}')"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 2: Algoritmo Avanzato con Anthropic

```yaml
variables:
  anthropic_api_key: "your-anthropic-key"

states:
  generate_sorting:
    state_type: "python_code_generator"
    prompt: "Implementa un algoritmo di merge sort ottimizzato per grandi dataset con analisi di complessità"
    max_steps: 25
    provider: "anthropic"
    model: "claude-3-sonnet-20240229"
    api_key: "{anthropic_api_key}"
    complexity_level: "expert"
    code_style: "google"
    include_documentation: true
    execution_mode: "full"
    output: "sorting_algorithm"
    success_transition: "benchmark"

  benchmark:
    state_type: "command"
    action:
      eval: |
        print(f"🎉 Algoritmo completato!")
        print(f"📊 Step eseguiti: {sorting_algorithm.steps_executed}")
        print(f"⏱️ Tempo: {sorting_algorithm.execution_time:.2f}s")
        print(f"🔄 Revisioni piano: {sorting_algorithm.plan_revisions}")
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 3: Solo Pianificazione

```yaml
states:
  plan_cache_system:
    state_type: "python_code_generator"
    prompt: "Pianifica lo sviluppo di un sistema di cache distribuito con Redis"
    max_steps: 15
    execution_mode: "plan_only"
    complexity_level: "expert"
    plan_output: "cache_plan"
    success_transition: "review_plan"

  review_plan:
    state_type: "command"
    action:
      eval: |
        print("📋 Piano di sviluppo:")
        for i, step in enumerate(cache_plan, 1):
            print(f"{i}. {step['title']}: {step['description']}")
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 4: Ollama Locale

```yaml
states:
  generate_with_ollama:
    state_type: "python_code_generator"
    prompt: "Crea una classe APIClient per REST API con retry logic"
    max_steps: 20
    provider: "ollama"
    model: "codellama"
    base_url: "http://localhost:11434"
    complexity_level: "medium"
    include_tests: true
    code_output: "api_client_code"
    tests_output: "api_client_tests"
    success_transition: "save_files"

  save_files:
    state_type: "file"
    action: "write"
    path: "generated_api_client.py"
    content: "{api_client_code}"
    transition: "save_tests"

  save_tests:
    state_type: "file"
    action: "write"
    path: "test_api_client.py"
    content: "{api_client_tests}"
    transition: "end"

  end:
    state_type: "end"
```

### 🆕 Esempio 5: Workspace Management

```yaml
variables:
  openai_api_key: "your-api-key"
  project_name: "calculator_app"

states:
  generate_with_workspace:
    state_type: "python_code_generator"
    prompt: "Crea una calcolatrice scientifica con interfaccia CLI"
    max_steps: 18
    provider: "openai"
    model: "gpt-3.5-turbo"
    api_key: "{openai_api_key}"
    
    # Configurazione Workspace
    workspace_enabled: true
    workspace_root: "my_projects"
    project_name: "{project_name}"
    timestamp_folders: true
    project_subfolder: true
    cleanup_on_error: false
    
    output: "calculator_result"
    success_transition: "show_workspace"

  show_workspace:
    state_type: "command"
    action:
      eval: |
        print(f"📁 Progetto creato in: {calculator_result.workspace_path}")
        print("📋 Struttura generata:")
        print("├── src/calculator_app.py")
        print("├── tests/test_calculator_app.py")
        print("├── docs/execution_plan.json")
        print("├── config/project_metadata.json")
        print("└── README.md")
    transition: "end"

  end:
    state_type: "end"
```

## 🔄 Flusso di Esecuzione

### Stati Interni del Plugin

1. **PLAN_CREATION** - Creazione piano di sviluppo (1 step)
2. **STEP_EXECUTION** - Esecuzione step del piano (N step)
3. **PLAN_REVIEW** - Revisione piano ogni 3 step (1 step per revisione)
4. **TEST_GENERATION** - Generazione test unitari (1 step)
5. **CODE_VALIDATION** - Validazione sintassi (1 step)
6. **EXECUTION** - Esecuzione codice (1 step)
7. **COMPLETION** - Finalizzazione risultati

### Conteggio Step

Il plugin conta tutti gli step nel limite configurato:

- ✅ Creazione piano iniziale
- ✅ Ogni step di generazione codice
- ✅ Revisioni del piano
- ✅ Generazione test
- ✅ Validazione sintassi
- ✅ Esecuzione finale

### Gestione Limiti

- **Warning**: A 80% del limite
- **Ottimizzazione**: Riduzione automatica step se necessario
- **Errore**: Ritorno risultati parziali se limite superato

## 📊 Output del Plugin

### Struttura Output Completo

```json
{
  "success": true,
  "generated_code": "# Codice Python generato...",
  "generated_tests": "# Test unitari...",
  "execution_plan": [
    {
      "title": "Step 1",
      "description": "Descrizione...",
      "components": ["comp1", "comp2"],
      "dependencies": []
    }
  ],
  "steps_executed": 15,
  "steps_remaining": 5,
  "plan_revisions": 2,
  "execution_time": 45.2,
  "performance_metrics": {
    "total_steps": 15,
    "step_times": [...],
    "average_step_time": 3.01
  },
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "timestamp": "2025-01-07T14:30:00"
}
```

### Output in Caso di Errore

```json
{
  "success": false,
  "error": "Step limit exceeded",
  "steps_executed": 20,
  "max_steps": 20,
  "partial_code": "# Codice parziale...",
  "partial_tests": "# Test parziali...",
  "execution_plan": [...]
}
```

## ⚙️ Configurazione Provider

### OpenAI

```yaml
provider: "openai"
model: "gpt-4"  # o gpt-3.5-turbo
api_key: "{openai_api_key}"
temperature: 0.3
```

**Modelli Supportati**: gpt-4, gpt-4-turbo, gpt-3.5-turbo, gpt-3.5-turbo-16k

### Anthropic

```yaml
provider: "anthropic"
model: "claude-3-sonnet-20240229"
api_key: "{anthropic_api_key}"
temperature: 0.3
```

**Modelli Supportati**: claude-3-opus, claude-3-sonnet, claude-3-haiku

### Ollama (Locale)

```yaml
provider: "ollama"
model: "codellama"
base_url: "http://localhost:11434"
temperature: 0.3
```

**Modelli Supportati**: codellama, llama2, mistral, neural-chat

## 📁 Workspace Management

### Funzionalità Workspace

Il plugin include un sistema avanzato di gestione workspace che organizza automaticamente i file generati in strutture di progetto professionali.

#### Struttura Workspace Automatica

```
workspace/
└── python-code-generator/
    └── projects/
        └── project_name_20250107_143000/
            ├── src/
            │   └── project_name.py          # Codice principale
            ├── tests/
            │   └── test_project_name.py     # Test unitari
            ├── docs/
            │   └── execution_plan.json      # Piano di sviluppo
            ├── config/
            │   └── project_metadata.json    # Metadati progetto
            └── README.md                     # Documentazione
```

#### Vantaggi del Workspace

- ✅ **Organizzazione**: Ogni progetto in una cartella dedicata
- ✅ **Sicurezza**: Nessun rischio di sovrascrivere file esistenti
- ✅ **Tracciabilità**: Timestamp e metadati per ogni generazione
- ✅ **Portabilità**: Facile spostare/condividere progetti
- ✅ **Pulizia**: Directory principale rimane ordinata

#### Configurazione Workspace

```yaml
# Configurazione completa workspace
generate_project:
  state_type: "python_code_generator"
  prompt: "Il tuo prompt qui"
  
  # Workspace settings
  workspace_enabled: true              # Abilita workspace (default: true)
  workspace_root: "my_workspace"       # Directory radice (default: "workspace")
  project_name: "my_project"           # Nome progetto (default: auto-generato)
  timestamp_folders: true              # Timestamp nei nomi (default: true)
  project_subfolder: true              # Sottocartelle strutturate (default: true)
  cleanup_on_error: false              # Pulizia su errore (default: false)
```

#### Disabilitare Workspace

```yaml
# Per salvare nella directory corrente (comportamento legacy)
generate_simple:
  state_type: "python_code_generator"
  prompt: "Il tuo prompt qui"
  workspace_enabled: false
```

#### Output Workspace

Quando il workspace è abilitato, l'output include il percorso del progetto:

```json
{
  "success": true,
  "workspace_path": "workspace/python-code-generator/projects/my_project_20250107_143000",
  "generated_code": "...",
  "generated_tests": "...",
  // ... altri campi
}
```

#### File Generati Automaticamente

Il workspace include file aggiuntivi per un progetto completo:

1. **Header Informativi**: Ogni file include metadati di generazione
2. **README.md**: Documentazione completa del progetto
3. **Metadati JSON**: Informazioni dettagliate sulla generazione
4. **Piano di Sviluppo**: JSON con il piano utilizzato

#### Esempio Completo con Workspace

```yaml
variables:
  openai_api_key: "your-key"

states:
  create_project:
    state_type: "python_code_generator"
    prompt: "Crea un sistema di gestione task con CLI"
    max_steps: 20
    api_key: "{openai_api_key}"
    
    # Workspace configuration
    workspace_enabled: true
    workspace_root: "generated_projects"
    project_name: "task_manager"
    timestamp_folders: true
    
    output: "project_result"
    success_transition: "setup_project"

  setup_project:
    state_type: "command"
    action:
      eval: |
        import os
        project_path = project_result.workspace_path
        
        # Crea file aggiuntivi
        with open(f"{project_path}/requirements.txt", "w") as f:
            f.write("click>=8.0.0\npytest>=7.0.0\n")
        
        with open(f"{project_path}/.gitignore", "w") as f:
            f.write("__pycache__/\n*.pyc\n.pytest_cache/\n")
        
        print(f"✅ Progetto completo creato in: {project_path}")
        print("📁 File disponibili:")
        for root, dirs, files in os.walk(project_path):
            level = root.replace(project_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    transition: "end"

  end:
    state_type: "end"
```

## 🧪 Testing e Validazione

### Validazione Automatica

Il plugin include validazione automatica:

- **Sintassi Python**: Parsing AST del codice generato
- **Test Syntax**: Validazione dei test generati
- **Esecuzione Sicura**: Test in namespace isolato

### Test Manuali

```bash
# Test sintassi
python -m py_compile generated_code.py

# Esecuzione test
python -m pytest test_generated.py

# Analisi qualità (se pylint installato)
pylint generated_code.py
```

## 🔧 Troubleshooting

### Errori Comuni

#### "Step limit exceeded"
```yaml
# Soluzione: Aumenta max_steps o riduci complessità
max_steps: 30
complexity_level: "simple"
```

#### "LangChain non installato"
```bash
pip install langchain openai anthropic
```

#### "Provider non supportato"
```yaml
# Verifica provider supportati
provider: "openai"  # openai, anthropic, ollama
```

#### "Errore di sintassi nel codice"
```yaml
# Abilita validazione e riprova
validate_syntax: true
temperature: 0.1  # Temperatura più bassa
```

### Debug e Logging

```yaml
# Abilita logging verboso
states:
  debug_generation:
    state_type: "python_code_generator"
    # ... altri parametri
    verbose: true
```

## 📈 Performance e Ottimizzazione

### Metriche Tipiche

- **Tempo Esecuzione**: 30-120 secondi
- **Utilizzo Memoria**: 50-200 MB
- **Token Usage**: 1000-5000 token
- **Step Medi**: 10-25 step

### Ottimizzazioni

```yaml
# Per velocità
temperature: 0.1
complexity_level: "simple"
include_tests: false

# Per qualità
temperature: 0.3
complexity_level: "expert"
max_steps: 30
```

## 🔒 Sicurezza

### Esecuzione Codice

- **Sandbox**: Esecuzione in namespace isolato
- **Validazione**: Controllo sintassi prima dell'esecuzione
- **Timeout**: Limite di tempo per prevenire loop infiniti

### Input Sanitization

- **Prompt Filtering**: Rimozione contenuti potenzialmente dannosi
- **Parameter Validation**: Controllo tipi e range parametri

## 🤝 Contributi e Supporto

### Repository

- **Plugin**: [intellyhub-plugins/python-code-generator](https://github.com/kuduk/intellyhub-plugins/tree/main/plugins/python-code-generator)
- **Issues**: [GitHub Issues](https://github.com/kuduk/intellyhub-plugins/issues)

### Sviluppo

```bash
# Clone repository
git clone https://github.com/kuduk/intellyhub-plugins.git
cd intellyhub-plugins/plugins/python-code-generator

# Test locale
python test_plugin.py
```

## 📄 Licenza

MIT License - Vedi [LICENSE](LICENSE) per dettagli.

## 🔄 Changelog

### v1.0.0 (2025-01-07)
- ✅ Rilascio iniziale
- ✅ Supporto multi-provider LLM
- ✅ Pianificazione step-by-step
- ✅ Controllo limiti step
- ✅ Generazione test automatica
- ✅ Validazione sintassi
- ✅ Metriche performance
- ✅ 🆕 Workspace Management con organizzazione automatica file
- ✅ 🆕 Strutture di progetto professionali
- ✅ 🆕 Metadati e documentazione automatica
- ✅ 🆕 Sicurezza percorsi e sanitizzazione nomi file

---

**Sviluppato con ❤️ per la community IntellyHub**
