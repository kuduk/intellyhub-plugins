# 💬 Plugin WeChat Work per IntellyHub

Plugin per inviare messaggi tramite API WeChat Work. Supporta l'invio di messaggi di testo, markdown e textcard a utenti, dipartimenti e gruppi specifici.

## 🚀 Caratteristiche

- ✅ **Invio messaggi di testo** semplici e formattati
- ✅ **Supporto Markdown** per messaggi ricchi
- ✅ **Messaggi TextCard** per contenuti strutturati
- ✅ **Destinatari multipli** (utenti, dipartimenti, tag)
- ✅ **Gestione automatica token** con refresh
- ✅ **Messaggi confidenziali** con flag safe
- ✅ **Gestione errori robusta** con retry
- ✅ **Logging dettagliato** per debugging

## 📋 Prerequisiti

### 1. Account WeChat Work
- Account aziendale WeChat Work attivo
- Applicazione creata nel pannello amministrativo
- Permessi di invio messaggi configurati

### 2. Credenziali Richieste
- **Corp ID**: ID dell'azienda WeChat Work
- **Corp Secret**: Secret dell'applicazione
- **Agent ID**: ID dell'agente/applicazione

### 3. Configurazione Ambiente
```bash
export WECHAT_CORP_ID="your_corp_id"
export WECHAT_CORP_SECRET="your_corp_secret"
export WECHAT_AGENT_ID="your_agent_id"
```

## 🛠️ Installazione

### Metodo 1: Package Manager IntellyHub
```bash
# Aggiungi al plugins.yaml
echo "dependencies:
  - wechat>=1.0.0" >> plugins.yaml

# Installa
python main.py plugins install
```

### Metodo 2: Installazione Manuale
```bash
# Copia i file nella directory corretta
cp -r intellyhub-plugins/plugins/wechat/ flow/states/
```

## 📖 Utilizzo

### Configurazione Base YAML

```yaml
variables:
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"

states:
  send_notification:
    state_type: wechat
    corp_id: "{corp_id}"
    corp_secret: "{corp_secret}"
    agent_id: "{agent_id}"
    to_user: "@all"
    message: "Ciao! Questo è un messaggio di test da IntellyHub."
    transition: end
  
  end:
    state_type: end
```

### Esempi Avanzati

#### 1. Messaggio a Utente Specifico
```yaml
send_to_user:
  state_type: wechat
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"
  to_user: "user123"
  message: "Messaggio personale per {user_name}"
  output: "wechat_result"
  success_transition: "log_success"
  error_transition: "handle_error"
```

#### 2. Messaggio a Dipartimento
```yaml
notify_department:
  state_type: wechat
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"
  to_party: "1"  # ID dipartimento
  message: "Notifica importante per il dipartimento IT"
  message_type: "text"
  transition: "next_step"
```

#### 3. Messaggio Markdown
```yaml
send_markdown:
  state_type: wechat
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"
  to_user: "@all"
  message: |
    # 📊 Rapporto Automatico
    
    **Status**: ✅ Completato
    **Timestamp**: {current_time}
    **Risultati**: {process_results}
    
    [Visualizza dettagli completi](https://dashboard.example.com)
  message_type: "markdown"
  transition: "end"
```

#### 4. Messaggio TextCard
```yaml
send_textcard:
  state_type: wechat
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"
  to_user: "manager123"
  message: |
    {
      "title": "Alert Sistema",
      "description": "Il sistema ha rilevato un'anomalia che richiede attenzione",
      "url": "https://monitoring.example.com/alert/123",
      "btntxt": "Visualizza Alert"
    }
  message_type: "textcard"
  transition: "end"
```

#### 5. Messaggio Confidenziale
```yaml
send_confidential:
  state_type: wechat
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"
  to_user: "ceo"
  message: "Informazioni riservate: {confidential_data}"
  safe: 1  # Messaggio confidenziale
  output: "secure_result"
  transition: "end"
```

## 🔧 Parametri di Configurazione

### Parametri Obbligatori
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `corp_id` | string | ID dell'azienda WeChat Work |
| `corp_secret` | string | Secret dell'applicazione |
| `agent_id` | string | ID dell'agente/applicazione |
| `message` | string | Testo del messaggio da inviare |

### Parametri Opzionali
| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `to_user` | string | "@all" | ID utente destinatario |
| `to_party` | string | "" | ID dipartimento destinatario |
| `to_tag` | string | "" | ID tag destinatario |
| `message_type` | string | "text" | Tipo messaggio (text/markdown/textcard) |
| `safe` | integer | 0 | Messaggio confidenziale (0=no, 1=sì) |
| `output` | string | - | Variabile per salvare risultato |
| `success_transition` | string | - | Stato successivo se successo |
| `error_transition` | string | - | Stato successivo se errore |

## 📊 Gestione Output

Il plugin può salvare il risultato in una variabile specificata:

```yaml
send_with_output:
  state_type: wechat
  # ... altri parametri ...
  output: "wechat_result"
  transition: "check_result"

check_result:
  state_type: if
  condition: "{wechat_result.success}"
  true_transition: "success_handler"
  false_transition: "error_handler"
```

### Struttura Output Successo
```json
{
  "success": true,
  "errcode": 0,
  "errmsg": "ok",
  "msgid": "message_id_from_wechat",
  "response_code": "response_code",
  "timestamp": 1692712345
}
```

### Struttura Output Errore
```json
{
  "success": false,
  "error": "Descrizione errore",
  "errcode": 40001,
  "errmsg": "invalid credential",
  "timestamp": 1692712345
}
```

## 🎯 Destinatari

### Tipi di Destinatari
- **Utente specifico**: `to_user: "user123"`
- **Tutti gli utenti**: `to_user: "@all"`
- **Dipartimento**: `to_party: "1"`
- **Tag**: `to_tag: "developers"`
- **Multipli**: Combina più parametri

### Esempi Destinatari
```yaml
# Utente singolo
to_user: "zhang.san"

# Multipli utenti (separati da |)
to_user: "zhang.san|li.si|wang.wu"

# Dipartimento IT
to_party: "2"

# Tag sviluppatori
to_tag: "dev_team"

# Combinazione
to_user: "manager"
to_party: "1"
to_tag: "urgent"
```

## 🔍 Tipi di Messaggio

### 1. Text (Testo Semplice)
```yaml
message_type: "text"
message: "Messaggio di testo semplice"
```

### 2. Markdown
```yaml
message_type: "markdown"
message: |
  # Titolo
  **Grassetto** e *corsivo*
  - Lista item 1
  - Lista item 2
  [Link](https://example.com)
```

### 3. TextCard
```yaml
message_type: "textcard"
message: |
  {
    "title": "Titolo Card",
    "description": "Descrizione dettagliata",
    "url": "https://example.com",
    "btntxt": "Apri"
  }
```

## 🚨 Gestione Errori

### Codici Errore Comuni
| Codice | Descrizione | Soluzione |
|--------|-------------|-----------|
| 40001 | Invalid credential | Verifica corp_id e corp_secret |
| 40013 | Invalid corpid | Controlla corp_id |
| 40014 | Invalid access_token | Token scaduto, verrà rinnovato automaticamente |
| 40054 | Invalid agentid | Verifica agent_id |
| 40003 | Invalid openid | Controlla to_user |

### Esempio Gestione Errori
```yaml
send_message:
  state_type: wechat
  # ... parametri ...
  output: "result"
  success_transition: "success"
  error_transition: "handle_error"

handle_error:
  state_type: if
  condition: "{result.errcode} == 40001"
  true_transition: "credential_error"
  false_transition: "generic_error"

credential_error:
  state_type: command
  action:
    eval: "print('Errore credenziali WeChat Work')"
  transition: "end"
```

## 🔐 Sicurezza

### Best Practices
1. **Variabili d'ambiente**: Usa sempre variabili d'ambiente per le credenziali
2. **Messaggi confidenziali**: Usa `safe: 1` per contenuti sensibili
3. **Validazione input**: Valida sempre i dati prima dell'invio
4. **Rate limiting**: Rispetta i limiti API di WeChat Work

### Esempio Sicuro
```yaml
variables:
  # Carica da variabili d'ambiente
  corp_id: "{WECHAT_CORP_ID}"
  corp_secret: "{WECHAT_CORP_SECRET}"
  agent_id: "{WECHAT_AGENT_ID}"

states:
  validate_data:
    state_type: if
    condition: "len('{sensitive_data}') > 0"
    true_transition: "send_secure"
    false_transition: "skip"
  
  send_secure:
    state_type: wechat
    corp_id: "{corp_id}"
    corp_secret: "{corp_secret}"
    agent_id: "{agent_id}"
    to_user: "{authorized_user}"
    message: "Dati sensibili: {sensitive_data}"
    safe: 1  # Messaggio confidenziale
    transition: "end"
```

## 🧪 Testing

### Test Base
```yaml
# test_wechat_basic.yaml
variables:
  test_message: "Test messaggio da IntellyHub"

states:
  test_send:
    state_type: wechat
    corp_id: "{WECHAT_CORP_ID}"
    corp_secret: "{WECHAT_CORP_SECRET}"
    agent_id: "{WECHAT_AGENT_ID}"
    to_user: "{WECHAT_TEST_USER}"
    message: "{test_message}"
    output: "test_result"
    transition: "check_result"
  
  check_result:
    state_type: command
    action:
      eval: "print(f'Risultato: {test_result}')"
    transition: "end"
  
  end:
    state_type: end
```

### Esecuzione Test
```bash
python main.py test_wechat_basic.yaml
```

## 📚 Risorse Utili

- [Documentazione API WeChat Work](https://developer.work.weixin.qq.com/document/path/90236)
- [Guida Setup WeChat Work](https://developer.work.weixin.qq.com/document/path/90665)
- [Codici Errore API](https://developer.work.weixin.qq.com/document/path/90313)

## 🤝 Supporto

- **Issues**: [GitHub Issues](https://github.com/kuduk/intellyhub-plugins/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/kuduk/intellyhub-plugins/discussions)
- **Email**: support@intellyhub.com

## 📄 Licenza

MIT License - vedi [LICENSE](../../../LICENSE) per dettagli.

---

**Sviluppato con ❤️ per IntellyHub**
