# IntellyHub Plugins Repository

Repository ufficiale dei plugin per IntellyHub - Sistema di automazione basato su diagrammi di flusso.

## Panoramica

Questo repository contiene una collezione di plugin che estendono le funzionalità di IntellyHub, permettendo l'integrazione con servizi esterni, API e sistemi di terze parti.

## Plugin Disponibili

### 🔵 Facebook Plugin v1.0.0
Plugin per pubblicare post su Facebook utilizzando l'API Graph.

**Caratteristiche:**
- ✅ Pubblicazione di post di testo
- ✅ Inclusione di link nei post  
- ✅ Pubblicazione programmata (scheduling)
- ✅ Gestione degli errori avanzata

**Installazione:**
```yaml
dependencies:
  - facebook>=1.0.0
```

[📖 Documentazione completa](./plugins/facebook/README.md)

### 📡 RSS Listener Plugin v1.0.0
Plugin listener per monitorare feed RSS e avviare automazioni sui nuovi articoli.

**Caratteristiche:**
- ✅ Monitoraggio multipli feed RSS
- ✅ Cache intelligente anti-duplicati
- ✅ Configurazione flessibile
- ✅ Estrazione dati completa
- ✅ Gestione errori robusta

**Installazione:**
```yaml
dependencies:
  - rss-listener>=1.0.0
```

[📖 Documentazione completa](./plugins/rss-listener/README.md)

### 📰 RSS Reader Plugin v1.0.0
Plugin stato per leggere feed RSS e filtrare articoli con oggetto Python strutturato.

**Caratteristiche:**
- ✅ Lettura RSS universale con filtro temporale
- ✅ Oggetto Python strutturato (RSSFeedResult/RSSArticle)
- ✅ Metodi di filtraggio avanzati (keyword, autore, tag, data)
- ✅ Ottimizzato per automatismi e integrazione
- ✅ Gestione errori robusta e performance ottimizzate

**Installazione:**
```yaml
dependencies:
  - rss-reader>=1.0.0
```

[📖 Documentazione completa](./plugins/rss-reader/README.md)

### 🤖 LLM Agent Plugin v1.0.0
Plugin universale per l'integrazione di modelli AI tramite LangChain.

**Caratteristiche:**
- ✅ Multi-Provider (OpenAI, Anthropic, Ollama, HuggingFace)
- ✅ LangChain Integration completa
- ✅ Chain Support (Simple, Conversation)
- ✅ Memory Management avanzata
- ✅ Cost Optimization con provider locali
- ✅ Flexible Prompting System

**Installazione:**
```yaml
dependencies:
  - llm-agent>=1.0.0
```

[📖 Documentazione completa](./plugins/llm-agent/README.md)

### 🐍 Python Code Generator Plugin v1.0.0
Plugin avanzato per la generazione automatica di codice Python con pianificazione step-by-step.

**Caratteristiche:**
- ✅ Pianificazione intelligente con controllo step
- ✅ Generazione codice iterativa con revisioni
- ✅ Test automatici inclusi nel conteggio step
- ✅ Multi-Provider LLM (OpenAI, Anthropic, Ollama)
- ✅ Validazione sintassi e qualità del codice
- ✅ Metriche dettagliate e performance tracking
- ✅ Modalità: plan_only, generate_only, full

**Installazione:**
```yaml
dependencies:
  - python-code-generator>=1.0.0
```

[📖 Documentazione completa](./plugins/python-code-generator/README.md)

### 🔗 LinkedIn Plugin v1.0.0
Plugin avanzato per estrarre dati pubblici da LinkedIn tramite web scraping.

**Caratteristiche:**
- ✅ Ricerca profili persone e aziende
- ✅ Filtri avanzati configurabili
- ✅ Doppia modalità scraping (Requests + Selenium)
- ✅ Integrazione LLM per analisi intelligente
- ✅ Anti-detection e gestione errori robusta
- ✅ Output strutturato JSON

**Installazione:**
```yaml
dependencies:
  - linkedin>=1.0.0
```

[📖 Documentazione completa](./plugins/linkedin/README.md)

### 🔊 Text-to-Speech Plugin v1.0.0
Plugin avanzato per convertire testo in audio utilizzando l'API di ElevenLabs.

**Caratteristiche:**
- ✅ Integrazione ElevenLabs API di alta qualità
- ✅ Supporto Multi-Voce e Multi-Lingua
- ✅ Gestione file automatica con timestamp
- ✅ Configurazione avanzata delle voci
- ✅ Output MP3 nella cartella workspace
- ✅ Gestione errori robusta e logging dettagliato

**Installazione:**
```yaml
dependencies:
  - text-to-speech>=1.0.0
```

[📖 Documentazione completa](./plugins/text-to-speech/README.md)

## Come Installare i Plugin

### Metodo 1: Package Manager (Raccomandato)

1. Crea un file `plugins.yaml` nel tuo progetto:
```yaml
dependencies:
  - facebook>=1.0.0
  - twitter>=2.0.0
```

2. Installa i plugin:
```bash
python -m package_manager install
```

### Metodo 2: Installazione Manuale

1. Scarica il plugin dalla directory `plugins/`
2. Copia il file `.py` in `flow/states/`
3. Riavvia l'applicazione

## Struttura di un Plugin

Ogni plugin è composto da:

```
plugins/nome_plugin/
├── manifest.json      # Metadati e configurazione
├── plugin_file.py     # Codice del plugin
└── README.md         # Documentazione
```

### Manifest.json Standard

Tutti i plugin seguono ora uno schema standardizzato per garantire coerenza e compatibilità:

```json
{
  "name": "nome_plugin",
  "version": "1.0.0",
  "description": "Descrizione dettagliata del plugin e delle sue funzionalità",
  "author": "IntellyHub Team",
  "license": "MIT",
  "entry_file": "nome_plugin_state.py",
  "state_type": "nome_plugin",
  "plugin_type": "state",
  "dependencies": {},
  "requirements": [
    "requests>=2.25.0"
  ],
  "api_version": "1.0",
  "tags": ["categoria", "funzionalità", "automazione"],
  "documentation": {
    "parameters": {
      "parametro_obbligatorio": {
        "type": "string",
        "required": true,
        "description": "Descrizione del parametro obbligatorio"
      },
      "parametro_opzionale": {
        "type": "string",
        "required": false,
        "default": "valore_default",
        "description": "Descrizione del parametro opzionale"
      },
      "output": {
        "type": "string",
        "required": false,
        "description": "Nome della variabile dove salvare il risultato"
      },
      "success_transition": {
        "type": "string",
        "required": false,
        "description": "Stato successivo in caso di successo"
      },
      "error_transition": {
        "type": "string",
        "required": false,
        "description": "Stato successivo in caso di errore"
      }
    },
    "examples": [
      {
        "name": "Esempio base",
        "description": "Descrizione dell'esempio",
        "config": {
          "state_type": "nome_plugin",
          "parametro_obbligatorio": "valore",
          "transition": "next_step"
        }
      }
    ]
  },
  "installation": {
    "instructions": [
      "1. Il plugin verrà installato automaticamente in flow/states/",
      "2. Configurare eventuali API keys necessarie",
      "3. Riavviare l'applicazione per caricare il plugin"
    ],
    "post_install": [
      "Verificare che il plugin sia caricato nei log di avvio"
    ],
    "environment_variables": [
      "API_KEY - chiave API necessaria per il funzionamento"
    ]
  },
  "compatibility": {
    "python_version": ">=3.7",
    "platforms": ["linux", "macos", "windows"]
  }
}
```

#### Parametri Standard per Tutti i Plugin

Ogni plugin supporta ora questi parametri standardizzati:

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `output` | string | Nome della variabile dove salvare il risultato dell'operazione |
| `success_transition` | string | Stato successivo in caso di successo |
| `error_transition` | string | Stato successivo in caso di errore |

## Creare un Nuovo Plugin

### 1. Struttura Base

```python
from .base_state import BaseState
import logging

logger = logging.getLogger(__name__)

class MioPlugin(BaseState):
    state_type = "mio_plugin"
    
    def execute(self, variables):
        # La tua logica qui
        return self.state_config.get("transition")
```

### 2. Utilizzo nel YAML

```yaml
states:
  mio_step:
    state_type: "mio_plugin"
    parametro: "valore"
    transition: "next_step"
```

### 3. Contribuire

1. Fork questo repository
2. Crea una nuova directory in `plugins/`
3. Aggiungi il tuo plugin con manifest e documentazione
4. Crea una Pull Request

## Esempi di Utilizzo

### Workflow Completo con Facebook

```yaml
# workflow_social.yaml
listener:
  type: "webhook"
  port: 8080

variables:
  facebook_token: "YOUR_TOKEN"
  page_id: "YOUR_PAGE_ID"

states:
  start:
    state_type: "facebook"
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "Nuovo post automatico! 🚀"
    link: "https://example.com"
    output: "result"
    success_transition: "success"
    error_transition: "error"

  success:
    state_type: "command"
    action:
      eval: "print(f'✅ Post pubblicato: {result.post_id}')"
    transition: "end"

  error:
    state_type: "command"
    action:
      eval: "print(f'❌ Errore: {result.error}')"
    transition: "end"

  end:
    state_type: "end"
```

## Plugin in Sviluppo

- 🔄 **Twitter Plugin** - Pubblicazione tweet e gestione timeline
- 🔄 **Instagram Plugin** - Pubblicazione foto e stories
- 🔄 **Telegram Plugin** - Invio messaggi e gestione bot
- 🔄 **Discord Plugin** - Integrazione con server Discord
- 🔄 **Slack Plugin** - Notifiche e automazioni workspace

## Requisiti di Sistema

- Python 3.8+
- IntellyHub Framework
- Dipendenze specifiche per ogni plugin (vedi manifest.json)

## Licenza

Questo repository è distribuito sotto licenza MIT. Ogni plugin può avere la propria licenza specifica.

## Supporto e Contributi

- 🐛 **Bug Reports**: [Apri un issue](https://github.com/kuduk/intellyhub-plugins/issues)
- 💡 **Feature Requests**: [Discussioni](https://github.com/kuduk/intellyhub-plugins/discussions)
- 🤝 **Contributi**: [Guida ai contributi](./CONTRIBUTING.md)

## Documentazione

- [📚 Documentazione IntellyHub](https://github.com/kuduk/ai-automation-fsm-py)
- [🔧 Guida Sviluppo Plugin](./PLUGIN_DEVELOPMENT.md)
- [📖 API Reference](./API_REFERENCE.md)

---

**Sviluppato con ❤️ dalla community IntellyHub**
