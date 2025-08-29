# Webhook Listener Plugin

Plugin listener per ricevere webhook HTTP. Espone endpoint HTTP e triggera workflow quando riceve richieste POST.

## Caratteristiche

- ✅ Server HTTP integrato
- ✅ Endpoint configurabile
- ✅ Supporto metodi HTTP multipli
- ✅ Validazione IP whitelisting
- ✅ Autenticazione tramite secret
- ✅ Headers personalizzati

## Configurazione

### Parametri Obbligatori

- `path`: Percorso endpoint (es. `/webhooks/my-hook`)

### Parametri Opzionali

- `port`: Porta server HTTP (default: 8080)
- `allowed_ips`: Array di IP autorizzati
- `secret`: Secret per validazione firma webhook

## Variabili Iniettate

- `webhook_data`: Dati ricevuti nel body della richiesta
- `webhook_headers`: Headers della richiesta HTTP
- `webhook_method`: Metodo HTTP (GET, POST, PUT, etc.)
- `webhook_ip`: Indirizzo IP del mittente

## Esempio di Utilizzo

```yaml
listener:
  type: webhook
  path: /webhooks/github
  port: 8080
  allowed_ips:
    - "192.30.252.0/22"
    - "185.199.108.0/22"
  secret: "{WEBHOOK_SECRET}"

states:
  - name: process_webhook
    type: command
    command: echo "Webhook ricevuto da $webhook_ip: $webhook_data"
```

## Integrazione con Servizi

### GitHub Webhooks
```yaml
listener:
  type: webhook
  path: /webhooks/github
  secret: "{GITHUB_WEBHOOK_SECRET}"
```

### GitLab Webhooks
```yaml
listener:
  type: webhook
  path: /webhooks/gitlab
  secret: "{GITLAB_WEBHOOK_SECRET}"
```

### Slack Webhooks
```yaml
listener:
  type: webhook
  path: /webhooks/slack
```

## Sicurezza

- Usa `allowed_ips` per limitare accesso
- Configura `secret` per validazione autenticità
- Usa HTTPS in produzione
- Monitora logs per tentativi di accesso non autorizzati

## Testing

Test locale con curl:
```bash
curl -X POST http://localhost:8080/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"message": "test webhook"}'
```