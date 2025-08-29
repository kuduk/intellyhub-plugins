# Email Listener Plugin

Plugin listener per ricevere messaggi email tramite IMAP. Monitora caselle email e triggera workflow automaticamente all'arrivo di nuovi messaggi.

## Caratteristiche

- ✅ Supporto protocollo IMAP
- ✅ Connessione SSL sicura
- ✅ Polling configurabile
- ✅ Filtraggio per cartella email
- ✅ Estrazione metadati completi

## Configurazione

### Parametri Obbligatori

- `server`: Server IMAP (es. `imap.gmail.com`)
- `username`: Username per autenticazione
- `password`: Password per autenticazione

### Parametri Opzionali

- `port`: Porta IMAP (default: 993)
- `folder`: Cartella da monitorare (default: "INBOX")
- `polling_interval`: Intervallo polling in secondi (default: 30)
- `use_ssl`: Usa connessione SSL (default: true)

## Variabili Iniettate

- `email_subject`: Oggetto dell'email ricevuta
- `email_from`: Indirizzo mittente
- `email_to`: Indirizzo destinatario
- `email_body`: Contenuto del messaggio
- `email_date`: Data e ora di ricezione
- `email_uid`: ID univoco del messaggio

## Esempio di Utilizzo

```yaml
listener:
  type: email
  server: imap.gmail.com
  username: "{EMAIL_USERNAME}"
  password: "{EMAIL_PASSWORD}"
  folder: INBOX
  polling_interval: 60

states:
  - name: process_email
    type: command
    command: echo "Ricevuta email da $email_from con oggetto: $email_subject"
```

## Provider Supportati

- Gmail (imap.gmail.com:993)
- Outlook (imap-mail.outlook.com:993)
- Yahoo (imap.mail.yahoo.com:993)
- Altri provider IMAP standard

## Sicurezza

⚠️ **Importante**: Usa variabili d'ambiente per credenziali sensibili:
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`

Non inserire mai credenziali direttamente nei file di configurazione.