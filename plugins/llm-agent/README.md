# LLM Agent Plugin per IntellyHub

Plugin universale per l'integrazione di modelli di linguaggio AI tramite LangChain. Supporta multipli provider come OpenAI, Anthropic, Ollama, HuggingFace e altri.

## 🤖 Caratteristiche

- ✅ **Multi-Provider**: OpenAI, Anthropic, Ollama, HuggingFace
- ✅ **LangChain Integration**: Sfrutta l'ecosistema LangChain
- ✅ **Chain Support**: Simple, Conversation, RAG (futuro)
- ✅ **Memory Management**: Buffer e Summary memory
- ✅ **Flexible Prompting**: System e User prompts personalizzabili
- ✅ **Cost Optimization**: Supporto provider locali (Ollama)
- ✅ **Error Handling**: Gestione errori robusta
- ✅ **Monitoring**: Tracking tempo esecuzione e performance

## 📋 Prerequisiti

### Dipendenze Python
```bash
pip install langchain>=0.1.0
pip install openai>=1.0.0        # Per OpenAI
pip install anthropic>=0.8.0     # Per Anthropic
pip install transformers>=4.30.0 # Per HuggingFace
pip install torch>=2.0.0         # Per HuggingFace
```

### Provider Setup

#### OpenAI
```bash
export OPENAI_API_KEY="your-api-key"
```

#### Anthropic
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

#### Ollama (Locale)
```bash
# Installa Ollama
curl -fsSL https://ollama.ai/install.sh | sh
# Scarica un modello
ollama pull llama2
```

## 🛠️ Installazione

### Tramite Package Manager (Raccomandato)

1. Aggiungi il plugin al file `plugins.yaml`:
```yaml
dependencies:
  - llm-agent>=1.0.0
```

2. Installa i plugin:
```bash
python -m package_manager install
```

### Installazione Manuale

1. Copia il file `llm_agent_state.py` nella directory `flow/states/`
2. Installa le dipendenze: `pip install langchain openai anthropic`
3. Riavvia l'applicazione

## ⚙️ Configurazione

### Parametri Base

```yaml
state_type: "llm_agent"
provider: "openai"              # openai, anthropic, ollama, huggingface
model: "gpt-4"                  # Modello specifico del provider
api_key: "{openai_api_key}"     # Chiave API (se necessaria)
temperature: 0.7                # Creatività (0.0-2.0)
max_tokens: 1000                # Lunghezza massima risposta
system_prompt: "Sei un assistente utile"
user_prompt: "Rispondi a: {question}"
output: "ai_response"           # Variabile output
```

### Parametri Avanzati

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `chain_type` | string | "simple" | Tipo di chain (simple, conversation) |
| `memory` | object | {} | Configurazione memoria |
| `chat_mode` | boolean | true | Usa chat models |
| `verbose` | boolean | false | Logging verboso |
| `base_url` | string | - | URL personalizzato |

## 📖 Esempi di Utilizzo

### Esempio 1: Chat OpenAI Semplice

```yaml
# openai_chat.yaml
variables:
  openai_api_key: "YOUR_OPENAI_KEY"
  user_question: "Spiega l'intelligenza artificiale"

states:
  ask_ai:
    state_type: "llm_agent"
    provider: "openai"
    model: "gpt-4"
    api_key: "{openai_api_key}"
    temperature: 0.7
    system_prompt: "Sei un esperto di tecnologia che spiega concetti complessi in modo semplice."
    user_prompt: "Domanda: {user_question}"
    output: "ai_response"
    transition: "show_result"

  show_result:
    state_type: "command"
    action:
      eval: "print(f'AI: {ai_response.response}')"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 2: Ollama Locale

```yaml
# ollama_local.yaml
variables:
  input_text: "Analizza questo codice Python"

states:
  analyze_code:
    state_type: "llm_agent"
    provider: "ollama"
    model: "llama2"
    base_url: "http://localhost:11434"
    temperature: 0.3
    user_prompt: "Analizza questo codice e suggerisci miglioramenti: {input_text}"
    response_key: "code_analysis"
    transition: "process_analysis"

  process_analysis:
    state_type: "command"
    action:
      eval: "print(f'Analisi: {code_analysis}')"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 3: Conversazione con Memoria

```yaml
# conversation_memory.yaml
variables:
  anthropic_api_key: "YOUR_ANTHROPIC_KEY"

states:
  chat_start:
    state_type: "llm_agent"
    provider: "anthropic"
    model: "claude-3-sonnet-20240229"
    api_key: "{anthropic_api_key}"
    chain_type: "conversation"
    memory:
      enabled: true
      type: "buffer"
    user_prompt: "Ciao, sono un nuovo utente"
    output: "chat_response"
    transition: "continue_chat"

  continue_chat:
    state_type: "llm_agent"
    provider: "anthropic"
    model: "claude-3-sonnet-20240229"
    api_key: "{anthropic_api_key}"
    chain_type: "conversation"
    memory:
      enabled: true
      type: "buffer"
    user_prompt: "Ricordi chi sono?"
    output: "chat_response2"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 4: Analisi Sentiment

```yaml
# sentiment_analysis.yaml
variables:
  openai_api_key: "YOUR_OPENAI_KEY"
  text_to_analyze: "Questo prodotto è fantastico!"

states:
  analyze_sentiment:
    state_type: "llm_agent"
    provider: "openai"
    model: "gpt-3.5-turbo"
    api_key: "{openai_api_key}"
    temperature: 0.1
    system_prompt: "Analizza il sentiment del testo e rispondi solo con: POSITIVO, NEGATIVO, o NEUTRO."
    user_prompt: "Testo: {text_to_analyze}"
    response_key: "sentiment"
    success_transition: "process_sentiment"
    error_transition: "handle_error"

  process_sentiment:
    state_type: "if"
    condition: "sentiment.strip() == 'POSITIVO'"
    true_transition: "positive_action"
    false_transition: "other_action"

  positive_action:
    state_type: "command"
    action:
      eval: "print('Sentiment positivo rilevato!')"
    transition: "end"

  other_action:
    state_type: "command"
    action:
      eval: "print(f'Sentiment: {sentiment}')"
    transition: "end"

  handle_error:
    state_type: "command"
    action:
      eval: "print('Errore nell\\'analisi sentiment')"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 5: Generazione Contenuti Social

```yaml
# content_generator.yaml
variables:
  openai_api_key: "YOUR_OPENAI_KEY"
  platform: "LinkedIn"
  topic: "Intelligenza Artificiale nel 2024"

states:
  generate_content:
    state_type: "llm_agent"
    provider: "openai"
    model: "gpt-4"
    api_key: "{openai_api_key}"
    temperature: 0.8
    max_tokens: 500
    system_prompt: "Sei un esperto di social media marketing. Crea contenuti coinvolgenti e professionali."
    user_prompt: "Crea un post per {platform} sul tema: {topic}. Includi hashtag appropriati e call-to-action."
    output: "generated_content"
    success_transition: "review_content"
    error_transition: "handle_error"

  review_content:
    state_type: "command"
    action:
      eval: "print(f'Contenuto generato:\\n{generated_content.response}')"
    transition: "post_to_social"

  post_to_social:
    state_type: "facebook"  # Usa il plugin Facebook
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "{generated_content.response}"
    transition: "end"

  handle_error:
    state_type: "command"
    action:
      eval: "print(f'Errore: {generated_content.error}')"
    transition: "end"

  end:
    state_type: "end"
```

## 🔧 Configurazioni Provider

### OpenAI
```yaml
provider: "openai"
model: "gpt-4"                    # gpt-4, gpt-4-turbo, gpt-3.5-turbo
api_key: "{openai_api_key}"
chat_mode: true
```

### Anthropic
```yaml
provider: "anthropic"
model: "claude-3-sonnet-20240229" # claude-3-opus, claude-3-sonnet, claude-3-haiku
api_key: "{anthropic_api_key}"
```

### Ollama (Locale)
```yaml
provider: "ollama"
model: "llama2"                   # llama2, codellama, mistral, neural-chat
base_url: "http://localhost:11434"
```

### HuggingFace
```yaml
provider: "huggingface"
model: "microsoft/DialoGPT-medium"
# Nessuna API key necessaria per modelli locali
```

## 🧪 Test e Debug

### Test Base
```bash
python main.py openai_chat.yaml
```

### Verifica Caricamento
Il plugin dovrebbe apparire nei log di avvio:
```
✅ Stato 'llm_agent' registrato dalla classe LLMAgentState
✅ Caricato llm_agent_state.py: 1 plugin trovati
```

### Debug Logging
```yaml
state_type: "llm_agent"
verbose: true  # Abilita logging verboso LangChain
```

## 📊 Output del Plugin

### Struttura Output Completo
```json
{
  "response": "Risposta del modello AI",
  "provider": "openai",
  "model": "gpt-4",
  "execution_time": 2.34,
  "timestamp": "2024-01-15T10:30:00",
  "success": true
}
```

### Variabili Create
- `{output}` - Output completo (se specificato)
- `{response_key}` - Solo la risposta (default: `llm_response`)

## ⚠️ Limitazioni e Considerazioni

### Limitazioni
- **API Costs**: Provider cloud hanno costi per token
- **Rate Limits**: Limiti di velocità per provider cloud
- **Model Availability**: Non tutti i modelli sono sempre disponibili
- **Memory Persistence**: La memoria non sopravvive al riavvio

### Best Practices
1. **Gestione API Keys**: Usa variabili d'ambiente per le chiavi
2. **Temperature Control**: Usa valori bassi (0.1-0.3) per task analitici
3. **Token Management**: Monitora l'uso dei token per controllo costi
4. **Error Handling**: Implementa sempre transizioni di errore
5. **Local Fallback**: Considera Ollama come fallback per ridurre costi

### Performance
- **OpenAI**: Veloce, costoso, alta qualità
- **Anthropic**: Veloce, costoso, ottimo per conversazioni
- **Ollama**: Lento, gratuito, privacy completa
- **HuggingFace**: Variabile, gratuito, richiede risorse locali

## 🔍 Risoluzione Problemi

### Errori Comuni

#### 1. LangChain Non Installato
**Errore**: `ImportError: LangChain è richiesto`

**Soluzione**: `pip install langchain`

#### 2. API Key Mancante
**Errore**: `Authentication failed`

**Soluzioni**:
- Verifica che l'API key sia corretta
- Controlla le variabili d'ambiente
- Verifica i permessi dell'API key

#### 3. Ollama Non Raggiungibile
**Errore**: `Connection refused to localhost:11434`

**Soluzioni**:
- Avvia Ollama: `ollama serve`
- Verifica che il modello sia scaricato: `ollama list`
- Controlla il base_url nella configurazione

#### 4. Modello Non Trovato
**Errore**: `Model not found`

**Soluzioni**:
- Verifica il nome del modello
- Per Ollama: `ollama pull model_name`
- Controlla la documentazione del provider

## 🚀 Casi d'Uso Avanzati

### 1. Content Pipeline
RSS → LLM Analysis → Social Media Posting

### 2. Customer Support
Email → Sentiment Analysis → Automated Response

### 3. Code Review
Git Webhook → Code Analysis → Slack Notification

### 4. Market Research
News Monitoring → Trend Analysis → Report Generation

### 5. Personal Assistant
Voice Input → Intent Recognition → Action Execution

## 📚 Riferimenti

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)

## 🤝 Supporto

Per problemi o domande:
- Apri un issue su [GitHub](https://github.com/kuduk/intellyhub-plugins)
- Consulta la documentazione LangChain
- Verifica i log di debug del plugin

## 📄 Licenza

Questo plugin è distribuito sotto licenza MIT.

---

**Sviluppato per IntellyHub - Sistema di Automazione Intelligente** 🚀
