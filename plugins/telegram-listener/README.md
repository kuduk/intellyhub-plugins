# 🤖 Telegram Listener Plugin

Plugin listener per IntellyHub che permette di ricevere messaggi da bot Telegram e triggerare workflow automaticamente.

## 📋 Descrizione

Il Telegram Listener utilizza il **long polling** dell'API Telegram per ascoltare messaggi in arrivo e avviare workflow in modo completamente automatico. Perfetto per creare bot Telegram intelligenti, sistemi di notifica bidirezionali e automazioni basate su messaggi.

## ✨ Caratteristiche

- **Long Polling Intelligente**: Utilizza l'API `getUpdates` con gestione ottimizzata degli offset
- **Filtraggio Avanzato**: Supporta filtri per chat_id, tipi di messaggio e utenti autorizzati
- **Gestione Errori Robusta**: Retry automatico e gestione degli errori di rete
- **Supporto Multi-Tipo**: Gestisce testi, foto, documenti, audio, video e altri tipi di messaggio
- **Variabili Automatiche**: Inietta automaticamente dati del messaggio nel workflow
- **Performance Ottimizzate**: Configurazioni flessibili per polling e timeout

## 🚀 Installazione

### Tramite Package Manager
```bash
python main.py plugins install telegram-listener
```

### Manuale
1. Copia la cartella `telegram-listener` in `intellyhub-plugins/plugins/`
2. Installa le dipendenze: `pip install requests>=2.25.0`
3. Riavvia IntellyHub

## 🔧 Configurazione

### Configurazione Base
```yaml
listener:
  type: "telegram"
  bot_token: "{TELEGRAM_BOT_TOKEN}"

variables:
  TELEGRAM_BOT_TOKEN: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

states:
  start:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "Hai scritto: {telegram_message_text}"
    transition: "end"
  
  end:
    state_type: "end"
```

### Configurazione Avanzata
```yaml
listener:
  type: "telegram"
  bot_token: "{TELEGRAM_BOT_TOKEN}"
  allowed_chat_ids: [123456789, 987654321]  # Solo chat autorizzate
  polling_interval: 1                       # Polling ogni secondo
  timeout: 60                              # Timeout lungo per gruppi attivi
  message_types: ["text", "photo"]         # Solo testi e foto
  ignore_old_messages: true                # Ignora messaggi precedenti

variables:
  TELEGRAM_BOT_TOKEN: "your_bot_token_here"

states:
  start:
    state_type: "switch"
    value: "{telegram_message_text}"
    cases:
      "/start": "welcome"
      "/help": "help"
      "/status": "status"
    default: "process_message"
  
  welcome:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: |
      🤖 <b>Benvenuto!</b>
      
      Sono un bot automatizzato. Comandi disponibili:
      /help - Mostra questo messaggio
      /status - Stato del sistema
    parse_mode: "HTML"
    transition: "end"
```

## 📊 Parametri di Configurazione

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `bot_token` | string | - | **Obbligatorio**. Token del bot Telegram |
| `allowed_chat_ids` | array | [] | Lista chat_id autorizzati (vuoto = tutti) |
| `polling_interval` | integer | 2 | Intervallo polling in secondi |
| `timeout` | integer | 30 | Timeout per richieste getUpdates |
| `message_types` | array | ["text"] | Tipi di messaggio da processare |
| `ignore_old_messages` | boolean | true | Ignora messaggi precedenti all'avvio |
| `download_voice` | boolean | true | Scarica automaticamente i messaggi vocali |
| `voice_download_path` | string | "workspace" | Cartella per salvare i file vocali |
| `transcribe_voice` | boolean | true | Abilita trascrizione automatica vocali |

### Tipi di Messaggio Supportati
- `text` - Messaggi di testo
- `photo` - Foto (con caption opzionale)
- `document` - Documenti e file
- `audio` - File audio
- `video` - Video (con caption opzionale)
- `voice` - Messaggi vocali
- `sticker` - Sticker
- `location` - Posizioni geografiche
- `contact` - Contatti

## 🔄 Variabili Iniettate

Il listener inietta automaticamente queste variabili nel workflow:

### Variabili Base (tutti i messaggi)
| Variabile | Descrizione | Esempio |
|-----------|-------------|---------|
| `telegram_message_text` | Testo del messaggio | "Ciao bot!" |
| `telegram_chat_id` | ID della chat | "123456789" |
| `telegram_user_id` | ID dell'utente | "987654321" |
| `telegram_message_id` | ID del messaggio | "42" |
| `telegram_user_first_name` | Nome utente | "Mario" |
| `telegram_user_last_name` | Cognome utente | "Rossi" |
| `telegram_user_username` | Username | "mariorossi" |
| `telegram_message_type` | Tipo messaggio | "text" |
| `telegram_message_date` | Timestamp messaggio | "1640995200" |
| `telegram_chat_type` | Tipo chat | "private" |
| `telegram_chat_title` | Titolo chat/gruppo | "Gruppo Test" |

### Variabili Vocali (solo per messaggi voice)
| Variabile | Descrizione | Esempio |
|-----------|-------------|---------|
| `telegram_voice_file_path` | Percorso completo del file vocale | "workspace/voice_20240824_041500_123_456_abc12345.ogg" |
| `telegram_voice_file_name` | Nome del file vocale | "voice_20240824_041500_123_456_abc12345.ogg" |
| `telegram_voice_file_size` | Dimensione del file in bytes | "15420" |
| `telegram_voice_duration` | Durata del vocale in secondi | "3" |
| `telegram_voice_mime_type` | Tipo MIME del file | "audio/ogg" |
| `telegram_voice_transcription` | Testo trascritto dal vocale | "Ciao, come stai?" |

## 📝 Esempi Pratici

### 1. Bot per Messaggi Vocali
```yaml
# telegram_voice_bot.yaml
listener:
  listener_type: "telegram"
  bot_token: "{TELEGRAM_BOT_TOKEN}"
  message_types: ["text", "voice"]  # Accetta testi e vocali
  download_voice: true              # Scarica vocali
  transcribe_voice: true            # Trascrivi vocali

variables:
  TELEGRAM_BOT_TOKEN: "your_token_here"

start_state: "start"

states:
  start:
    state_type: "if"
    condition: "'{telegram_message_type}' == 'voice'"
    true_transition: "handle_voice"
    false_transition: "handle_text"
  
  handle_voice:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: |
      🎤 <b>Vocale ricevuto!</b>
      
      📁 File: <code>{telegram_voice_file_name}</code>
      ⏱️ Durata: {telegram_voice_duration}s
      🎯 Trascrizione: <i>"{telegram_voice_transcription}"</i>
    parse_mode: "HTML"
    transition: "end"
  
  handle_text:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "💬 Testo: {telegram_message_text}"
    transition: "end"
  
  end:
    state_type: "end"
```

### 2. Bot Echo Semplice
```yaml
# telegram_echo_bot.yaml
listener:
  type: "telegram"
  bot_token: "{TELEGRAM_BOT_TOKEN}"

variables:
  TELEGRAM_BOT_TOKEN: "your_token_here"

states:
  start:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "🔄 Echo: {telegram_message_text}"
    transition: "end"
  
  end:
    state_type: "end"
```

### 2. Bot con Comandi
```yaml
# telegram_command_bot.yaml
listener:
  type: "telegram"
  bot_token: "{TELEGRAM_BOT_TOKEN}"

variables:
  TELEGRAM_BOT_TOKEN: "your_token_here"

states:
  start:
    state_type: "if"
    condition: "'{telegram_message_text}'.startswith('/')"
    true_transition: "handle_command"
    false_transition: "handle_message"
  
  handle_command:
    state_type: "switch"
    value: "{telegram_message_text}"
    cases:
      "/start": "cmd_start"
      "/help": "cmd_help"
      "/time": "cmd_time"
    default: "cmd_unknown"
  
  cmd_start:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: |
      🚀 <b>Bot avviato!</b>
      
      Benvenuto {telegram_user_first_name}!
      Usa /help per vedere i comandi disponibili.
    parse_mode: "HTML"
    transition: "end"
  
  cmd_help:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: |
      📚 <b>Comandi disponibili:</b>
      
      /start - Avvia il bot
      /help - Mostra questo messaggio
      /time - Mostra l'ora corrente
    parse_mode: "HTML"
    transition: "end"
  
  cmd_time:
    state_type: "command"
    action:
      eval: "import datetime; datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')"
    output: "current_time"
    transition: "send_time"
  
  send_time:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "🕐 Ora corrente: {current_time}"
    transition: "end"
  
  cmd_unknown:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "❓ Comando non riconosciuto. Usa /help per vedere i comandi disponibili."
    transition: "end"
  
  handle_message:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "💬 Hai scritto: {telegram_message_text}"
    transition: "end"
  
  end:
    state_type: "end"
```

### 3. Bot con Integrazione AI
```yaml
# telegram_ai_assistant.yaml
listener:
  type: "telegram"
  bot_token: "{TELEGRAM_BOT_TOKEN}"
  allowed_chat_ids: [123456789]  # Solo il tuo chat_id

variables:
  TELEGRAM_BOT_TOKEN: "your_token_here"
  OPENAI_API_KEY: "your_openai_key"

states:
  start:
    state_type: "if"
    condition: "'{telegram_message_text}'.startswith('/ai ')"
    true_transition: "process_ai_request"
    false_transition: "normal_response"
  
  process_ai_request:
    state_type: "command"
    action:
      eval: "'{telegram_message_text}'[4:]"  # Rimuovi '/ai '
    output: "ai_prompt"
    transition: "call_ai"
  
  call_ai:
    state_type: "llm_agent"
    provider: "openai"
    api_key: "{OPENAI_API_KEY}"
    model: "gpt-3.5-turbo"
    prompt: "{ai_prompt}"
    output: "ai_response"
    success_transition: "send_ai_response"
    error_transition: "ai_error"
  
  send_ai_response:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "🤖 AI: {ai_response}"
    transition: "end"
  
  ai_error:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "❌ Errore nell'elaborazione AI. Riprova più tardi."
    transition: "end"
  
  normal_response:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: |
      👋 Ciao {telegram_user_first_name}!
      
      Per usare l'AI, scrivi: /ai [la tua domanda]
      Esempio: /ai Spiegami la fotosintesi
    transition: "end"
  
  end:
    state_type: "end"
```

## 🔧 Setup del Bot Telegram

### 1. Creare il Bot
1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot`
3. Scegli un nome per il bot (es. "Il Mio Bot")
4. Scegli un username (es. "ilmiobot_bot")
5. Copia il token fornito

### 2. Ottenere il Chat ID
```bash
# Metodo 1: Invia un messaggio al bot e usa questo URL
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# Metodo 2: Usa il bot @userinfobot su Telegram
```

### 3. Testare la Connessione
```bash
# Verifica che il bot sia attivo
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

## 🔍 Troubleshooting

### Problemi Comuni

**Bot non risponde:**
- Verifica che il token sia corretto
- Controlla che il bot sia avviato con `/start`
- Verifica i log per errori di connessione

**Messaggi non arrivano:**
- Controlla il filtro `allowed_chat_ids`
- Verifica il filtro `message_types`
- Controlla che `ignore_old_messages` sia configurato correttamente

**Errori di timeout:**
- Riduci il valore di `timeout`
- Aumenta `polling_interval`
- Verifica la connessione internet

### Log di Debug
```yaml
# Abilita logging dettagliato
logging:
  level: DEBUG
  handlers:
    - console
    - file
```

## 🔗 Integrazione con Altri Plugin

### Con Telegram Bot (per risposte)
```yaml
states:
  respond:
    state_type: "telegram-bot"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{telegram_chat_id}"
    message: "Risposta automatica"
```

### Con LLM Agent (per AI)
```yaml
states:
  ai_process:
    state_type: "llm_agent"
    provider: "openai"
    prompt: "{telegram_message_text}"
    output: "ai_response"
```

### Con RSS Reader (per notifiche)
```yaml
states:
  check_news:
    state_type: "rss_reader"
    url: "https://feeds.example.com/news.xml"
    output: "news_items"
```

## 📈 Performance e Scalabilità

### Configurazioni Ottimizzate

**Per bot personali:**
```yaml
polling_interval: 1
timeout: 30
message_types: ["text"]
```

**Per bot di gruppo:**
```yaml
polling_interval: 3
timeout: 60
message_types: ["text"]
allowed_chat_ids: [group_id]
```

**Per bot ad alto traffico:**
```yaml
polling_interval: 0.5
timeout: 10
message_types: ["text"]
# Considera l'uso di webhook invece del polling
```

## 🛡️ Sicurezza

### Best Practices
- Usa sempre `allowed_chat_ids` per limitare l'accesso
- Non esporre il bot token nei log
- Implementa rate limiting se necessario
- Valida sempre gli input degli utenti

### Esempio di Validazione
```yaml
states:
  validate_input:
    state_type: "if"
    condition: "len('{telegram_message_text}') < 1000"
    true_transition: "process_message"
    false_transition: "message_too_long"
```

## 📚 Risorse Utili

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BotFather](https://t.me/botfather)
- [IntellyHub Documentation](../../../documentazione/)

## 🤝 Supporto

- **Issues**: [GitHub Issues](https://github.com/kuduk/intellyhub-plugins/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/kuduk/intellyhub-plugins/discussions)
- **Email**: support@intellyhub.com

## 📄 Licenza

MIT License - vedi [LICENSE](../../../LICENSE) per dettagli.

---

**Creato con ❤️ per la community IntellyHub**
