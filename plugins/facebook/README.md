# Plugin Facebook per IntellyHub

Plugin per pubblicare post su Facebook utilizzando l'API Graph di Facebook. Supporta post di testo, link e pubblicazione programmata.

## Caratteristiche

- ✅ Pubblicazione di post di testo
- ✅ Inclusione di link nei post
- ✅ Pubblicazione programmata (scheduling)
- ✅ Gestione degli errori con transizioni personalizzate
- ✅ Output dettagliato con ID del post e stato dell'operazione

## Prerequisiti

### 1. Token di Accesso Facebook

Per utilizzare questo plugin, è necessario ottenere un token di accesso Facebook:

1. Vai su [Facebook Developers](https://developers.facebook.com/)
2. Crea una nuova app o usa una esistente
3. Aggiungi il prodotto "Facebook Login"
4. Genera un token di accesso con i permessi:
   - `pages_manage_posts` - per pubblicare sui post
   - `pages_read_engagement` - per leggere le informazioni della pagina

### 2. ID della Pagina Facebook

Ottieni l'ID della pagina Facebook:
1. Vai sulla tua pagina Facebook
2. Clicca su "Informazioni" nella barra laterale sinistra
3. Scorri fino alla sezione "Altro" per trovare l'ID della pagina

## Installazione

### Tramite Package Manager

1. Aggiungi il plugin al file `plugins.yaml`:
```yaml
dependencies:
  - facebook>=1.0.0
```

2. Installa i plugin:
```bash
python -m package_manager install
```

### Installazione Manuale

1. Copia il file `facebook_state.py` nella directory `flow/states/`
2. Riavvia l'applicazione per caricare il plugin

## Configurazione

### Parametri Obbligatori

- `access_token`: Token di accesso Facebook
- `page_id`: ID della pagina Facebook

### Parametri Opzionali

- `message`: Testo del post
- `link`: URL da includere nel post
- `scheduled_publish_time`: Data/ora di pubblicazione programmata
- `output`: Nome della variabile per salvare il risultato
- `success_transition`: Stato successivo in caso di successo
- `error_transition`: Stato successivo in caso di errore

## Esempi di Utilizzo

### Post Semplice

```yaml
states:
  publish_post:
    state_type: "facebook"
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "Ciao dal mio bot automatizzato! 🤖"
    transition: "next_step"
```

### Post con Link

```yaml
states:
  share_link:
    state_type: "facebook"
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "Scopri questo fantastico progetto open source!"
    link: "https://github.com/kuduk/intellyhub-plugins"
    output: "facebook_result"
    success_transition: "success"
    error_transition: "handle_error"
```

### Post Programmato

```yaml
states:
  scheduled_post:
    state_type: "facebook"
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "Post programmato per domani mattina!"
    scheduled_publish_time: "2024-01-15T09:00:00"
    output: "result"
    transition: "check_result"
```

### Formati Data Supportati

Il plugin supporta diversi formati per `scheduled_publish_time`:

- **ISO 8601**: `2024-01-15T10:30:00` o `2024-01-15T10:30:00Z`
- **Formato standard**: `2024-01-15 10:30:00`
- **Formato italiano**: `15/01/2024 10:30`
- **Timestamp Unix**: `1705312200`

## Gestione degli Errori

Il plugin fornisce informazioni dettagliate sugli errori:

```yaml
states:
  publish_post:
    state_type: "facebook"
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "Test post"
    output: "result"
    success_transition: "success"
    error_transition: "handle_error"

  handle_error:
    state_type: "command"
    action:
      eval: "print(f'Errore: {result.error}')"
    transition: "end"
```

## Output del Plugin

Quando si specifica il parametro `output`, il plugin salva un oggetto con le seguenti informazioni:

### In caso di successo:
```json
{
  "post_id": "123456789_987654321",
  "success": true,
  "message": "Post pubblicato con successo",
  "scheduled": false
}
```

### In caso di errore:
```json
{
  "success": false,
  "error": "Descrizione dell'errore",
  "status_code": 400
}
```

## Risoluzione Problemi

### Errore di Autenticazione
- Verifica che il token di accesso sia valido e non scaduto
- Controlla che il token abbia i permessi necessari

### Errore di Pagina Non Trovata
- Verifica che l'ID della pagina sia corretto
- Assicurati che il token abbia accesso alla pagina specificata

### Errore di Pubblicazione Programmata
- Controlla che la data sia nel futuro
- Verifica il formato della data
- I post programmati richiedono permessi aggiuntivi

## Limitazioni

- Il plugin supporta solo post di testo e link (no immagini/video)
- È necessario un token di accesso valido con i permessi appropriati
- La pubblicazione programmata ha limitazioni temporali di Facebook (max 6 mesi nel futuro)

## Supporto

Per problemi o domande:
- Apri un issue su [GitHub](https://github.com/kuduk/intellyhub-plugins)
- Consulta la [documentazione di Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
