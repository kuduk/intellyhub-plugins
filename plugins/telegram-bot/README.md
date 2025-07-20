# Telegram Bot Plugin per IntellyHub

Plugin per inviare messaggi tramite bot Telegram nelle tue automazioni IntellyHub.

## Installazione

```bash
# Installa il plugin
python main.py plugins install

# O copia manualmente nella directory plugins
cp -r telegram-bot/ intellyhub-plugins/plugins/
```

## Configurazione

### 1. Crea un bot Telegram

1. Avvia una chat con [@BotFather](https://t.me/botfather)
2. Invia `/newbot` e segui le istruzioni
3. Salva il **token del bot** che ti verrà fornito

### 2. Ottieni il chat ID

1. Avvia una chat con il tuo bot
2. Invia un messaggio qualsiasi
3. Visita: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Trova il tuo **chat_id** nella risposta (sarà un numero negativo per gruppi)

## Utilizzo

### Esempio base

```yaml
start_state: send_message
variables:
  TELEGRAM_BOT_TOKEN: "123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
  TELEGRAM_CHAT_ID: "-1001234567890"
  message_text: "🚀 Automazione completata con successo!"

states:
  send_message:
    state_type: telegram
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{TELEGRAM_CHAT_ID}"
    message: "{message_text}"
    transition: end

  end:
    state_type: end
```

### Esempio avanzato con output

```yaml
start_state: send_notification
variables:
  bot_token: "{TELEGRAM_BOT_TOKEN}"
  chat_id: "{TELEGRAM_CHAT_ID}"
  workflow_name: "RSS Monitor"
  articles_count: 5

states:
  send_notification:
    state_type: telegram
    bot_token: "{bot_token}"
    chat_id: "{chat_id}"
    message: |
      <b>📊 {workflow_name} Update</b>
      
      ✅ Processati {articles_count} nuovi articoli
      🕐 {timestamp}
      
      <i>Automazione IntellyHub</i>
    parse_mode: HTML
    disable_notification: false
    output: telegram_result
    success_transition: log_success
    error_transition: handle_error

  log_success:
    state_type: command
    action:
      eval: |
        print(f"📱 Messaggio inviato! ID: {telegram_result['message_id']}")
    transition: end

  handle_error:
    state_type: command
    action:
      eval: |
        print(f"❌ Errore Telegram: {telegram_result['error']}")
    transition: end

  end:
    state_type: end
```

### Esempio con messaggio dinamico

```yaml
start_state: build_message
variables:
  bot_token: "{TELEGRAM_BOT_TOKEN}"
  chat_id: "{TELEGRAM_CHAT_ID}"
  alert_type: "warning"
  temperature: 28.5
  humidity: 65

states:
  build_message:
    state_type: command
    action:
      eval: |
        telegram_message = f"""
🌡️ <b>Alert Meteo</b>

Tipo: {alert_type}
Temperatura: {temperature}°C
Umidità: {humidity}%

⚠️ Condizioni critiche rilevate!
        """
    transition: send_alert

  send_alert:
    state_type: telegram
    bot_token: "{bot_token}"
    chat_id: "{chat_id}"
    message: "{telegram_message}"
    parse_mode: HTML
    transition: end

  end:
    state_type: end
```

## Parametri di configurazione

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `bot_token` | string | - | Token del bot Telegram (obbligatorio) |
| `chat_id` | string | - | ID della chat di destinazione (obbligatorio) |
| `message` | string | - | Testo del messaggio da inviare (obbligatorio) |
| `parse_mode` | string | "HTML" | Modalità di parsing: "HTML", "Markdown", "MarkdownV2" |
| `disable_notification` | boolean | false | Disabilita la notifica sonora |
| `output` | string | - | Nome variabile per salvare il risultato |

## Formattazione messaggi

### HTML supportato
```html
<b>grassetto</b>
<i>corsivo</i>
<u>sottolineato</u>
<s>barrato</s>
<code>codice</code>
<pre>blocco codice</pre>
<a href="http://www.example.com/">link</a>
```

### Markdown supportato
```markdown
*grassetto* o **grassetto**
_corsivo_ o __corsivo__
`codice`
[testo link](URL)
```

## Gestione errori

Il plugin gestisce automaticamente:
- Token non validi
- Chat ID non validi
- Messaggi troppo lunghi (>4096 caratteri)
- Errori di rete
- Rate limiting

## Variabili di output

Quando specifichi `output: nome_variabile`, riceverai:

```json
{
  "success": true,
  "message_id": 123456789,
  "chat_id": -1001234567890,
  "timestamp": 1625097600
}
```

In caso di errore:

```json
{
  "success": false,
  "error": "Descrizione dell'errore"
}
```

## Troubleshooting

### Errore "chat not found"
- Assicurati che il bot sia stato aggiunto al gruppo/canale
- Verifica che il chat_id sia corretto

### Errore "bot token invalid"
- Controlla che il token sia completo e corretto
- Verifica che il bot non sia stato eliminato

### Messaggio non formattato correttamente
- Usa `parse_mode: HTML` per HTML
- Usa `parse_mode: Markdown` per Markdown
- Escapa i caratteri speciali quando necessario
