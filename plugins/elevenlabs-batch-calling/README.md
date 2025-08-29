# ElevenLabs Batch Calling Plugin

Plugin per IntellyHub che consente di gestire batch calls di ElevenLabs Conversational AI. Supporta la creazione, monitoraggio e gestione di campagne di chiamate automatizzate.

## Funzionalità

- **Submit Batch Call**: Crea e sottomette un nuovo job di batch calling
- **Get Batch Status**: Recupera informazioni dettagliate su un batch job esistente  
- **List Batch Jobs**: Lista tutti i job di batch calling nel workspace
- **Gestione errori robusta**: Logging dettagliato e gestione di tutti i tipi di errore
- **Supporto per programmazione**: Possibilità di programmare chiamate per il futuro
- **Integrazione completa**: Compatibile con il sistema di workflow di IntellyHub

## Prerequisiti

1. **Account ElevenLabs** con Conversational AI attivo
2. **Agent configurato** in ElevenLabs
3. **Numero di telefono** configurato per l'agent
4. **API Key** di ElevenLabs

## Installazione

### Tramite Package Manager

```bash
python main.py plugins install elevenlabs-batch-calling
```

### Installazione Manuale

1. Copia la cartella `elevenlabs-batch-calling` nella directory `intellyhub-plugins/plugins/`
2. Installa la dipendenza richiesta: `pip install requests>=2.25.0`
3. Riavvia l'applicazione IntellyHub

## Configurazione

### Variabili d'ambiente

```bash
export ELEVENLABS_API_KEY="your_elevenlabs_api_key"
```

### Parametri nel workflow

I parametri possono essere configurati direttamente nel YAML del workflow utilizzando la sintassi `{VARIABILE}`.

## Utilizzo

### Operazioni Supportate

Il plugin supporta tre operazioni principali controllate dal parametro `operation`:

#### 1. Submit Batch Call (`operation: "submit"`)

Crea un nuovo job di batch calling.

**Parametri obbligatori:**
- `api_key`: API key di ElevenLabs
- `call_name`: Nome del job di batch calling
- `agent_id`: ID dell'agent ElevenLabs
- `agent_phone_number_id`: ID del numero di telefono dell'agent
- `recipients`: Array di oggetti recipients con supporto per strutture annidate (vedi sezione "Struttura Recipients")

**Parametri opzionali:**
- `scheduled_time_unix`: Timestamp Unix per programmare le chiamate (null per immediate)

#### 2. Get Batch Status (`operation: "get"`)

Recupera informazioni dettagliate su un batch job esistente.

**Parametri obbligatori:**
- `api_key`: API key di ElevenLabs
- `batch_id`: ID del batch job da recuperare

#### 3. List Batch Jobs (`operation: "list"`)

Lista tutti i job di batch calling nel workspace.

**Parametri obbligatori:**
- `api_key`: API key di ElevenLabs

**Parametri opzionali:**
- `limit`: Numero massimo di job da recuperare (default: 100)
- `last_doc`: Token di paginazione per continuare la lista

## Struttura Recipients

Il parametro `recipients` utilizza **array nativi con oggetti annidati** per massima flessibilità e migliore UX nel frontend.

### 🏗️ Architettura Gerarchica

Ogni recipient supporta una struttura a 4 livelli:

```yaml
recipients:
  - phone_number: "+1234567890"          # OBBLIGATORIO
    contact_info:                        # Informazioni contatto
      name: "Mario Rossi"
      company: "ABC Corp"
      title: "CEO" 
      department: "Executive"
    preferences:                         # Preferenze comunicazione
      language: "it"
      timezone: "Europe/Rome"
      best_call_times:
        - "09:00-12:00"
        - "14:00-18:00" 
      blackout_dates:
        - "2025-08-15"
        - "2025-12-25"
    metadata:                           # Metadati personalizzati
      priority: "high"
      customer_type: "vip"
      tags:
        - "italian"
        - "enterprise"
      custom_fields:
        account_value: "1000000"
        contract_type: "Enterprise"
```

### 📋 Livelli di Complessità

#### Livello 1: Minimale
```yaml
recipients:
  - phone_number: "+1234567890"
  - phone_number: "+0987654321"
```

#### Livello 2: Con Nome
```yaml
recipients:
  - phone_number: "+1234567890"
    contact_info:
      name: "Mario Rossi"
  - phone_number: "+0987654321"
    contact_info:
      name: "John Smith"
```

#### Livello 3: Contact Info Completo
```yaml
recipients:
  - phone_number: "+1234567890"
    contact_info:
      name: "Mario Rossi"
      company: "Italian Corp" 
      title: "Sales Director"
      department: "Sales"
```

#### Livello 4: Con Preferences
```yaml
recipients:
  - phone_number: "+1234567890"
    contact_info:
      name: "Mario Rossi"
      company: "Italian Corp"
    preferences:
      language: "it"
      timezone: "Europe/Rome"
      best_call_times:
        - "09:00-12:00"
        - "14:00-18:00"
```

#### Livello 5: Completo con Metadata
```yaml
recipients:
  - phone_number: "+1234567890"
    contact_info:
      name: "Mario Rossi"
      company: "Italian Corp"
      title: "CEO"
    preferences:
      language: "it"
      timezone: "Europe/Rome"
    metadata:
      priority: "urgent"
      customer_type: "vip"
      tags: ["enterprise", "decision-maker"]
      custom_fields:
        account_value: "1000000"
        last_interaction: "2025-01-15"
```

### 📊 Campi Supportati

#### 📱 `phone_number` (Obbligatorio)
- Formato: `+[country][number]` (es. `+1234567890`)
- Validazione: Pattern regex internazionale

#### 👤 `contact_info` (Opzionale)
- `name`: Nome completo del contatto
- `company`: Nome dell'azienda  
- `title`: Titolo/ruolo (es. "CEO", "Manager")
- `department`: Dipartimento (es. "Sales", "IT")

#### ⚙️ `preferences` (Opzionale)
- `language`: Codice ISO lingua (`it`, `en`, `es`, `fr`, ecc.)
- `timezone`: Timezone IANA (`Europe/Rome`, `America/New_York`)
- `best_call_times`: Array di fasce orarie (`["09:00-12:00", "14:00-18:00"]`)
- `blackout_dates`: Array di date esclusione (`["2025-08-15", "2025-12-25"]`)

#### 📊 `metadata` (Opzionale)
- `priority`: Priorità contatto (`low`, `medium`, `high`, `urgent`)
- `customer_type`: Tipo cliente (`prospect`, `customer`, `vip`, `partner`)
- `tags`: Array di tag personalizzati
- `custom_fields`: Oggetto con campi personalizzati liberi

### 🔄 Supporto Variabili

Tutti i campi supportano la sostituzione con variabili:

```yaml
recipients:
  - phone_number: "{customer_phone}"
    contact_info:
      name: "{customer_name}"
      company: "{customer_company}"
    preferences:
      language: "{customer_language}"
    metadata:
      priority: "{customer_priority}"
      custom_fields:
        account_value: "{account_value}"
        region: "{customer_region}"
```

## Esempi

### Esempio 1: Submit Batch Call (Minimale)

```yaml
variables:
  ELEVENLABS_API_KEY: "your_api_key_here"
  
states:
  create_batch_call:
    state_type: "elevenlabs_batch_calling"
    operation: "submit"
    api_key: "{ELEVENLABS_API_KEY}"
    call_name: "Marketing Campaign Q1 2025"
    agent_id: "your-agent-id"
    agent_phone_number_id: "your-phone-number-id"
    recipients:
      - phone_number: "+1234567890"
      - phone_number: "+0987654321"
      - phone_number: "+1111111111"
    scheduled_time_unix: null  # Immediate
    output: "batch_result"
    success_transition: "monitor_batch"
    error_transition: "handle_error"
    
  monitor_batch:
    state_type: "elevenlabs_batch_calling"
    operation: "get"
    api_key: "{ELEVENLABS_API_KEY}"
    batch_id: "{batch_result.batch_id}"
    output: "batch_status"
    transition: "end"
    
  handle_error:
    state_type: "command"
    action:
      eval: "print(f'Errore: {batch_result.error}')"
    transition: "end"
    
  end:
    state_type: "end"
```

### Esempio 2: Batch Call con Oggetti Annidati

```yaml
variables:
  ELEVENLABS_API_KEY: "your_api_key_here"
  
states:
  create_advanced_batch:
    state_type: "elevenlabs_batch_calling"
    operation: "submit"
    api_key: "{ELEVENLABS_API_KEY}"
    call_name: "Advanced Customer Survey"
    agent_id: "your-agent-id" 
    agent_phone_number_id: "your-phone-number-id"
    recipients:
      - phone_number: "+1234567890"
        contact_info:
          name: "Mario Rossi"
          company: "Italian Corp"
          title: "CEO"
        preferences:
          language: "it"
          timezone: "Europe/Rome"
          best_call_times:
            - "09:00-12:00"
            - "14:00-18:00"
        metadata:
          priority: "high"
          customer_type: "vip"
          tags:
            - "italian"
            - "enterprise"
          custom_fields:
            account_value: "1000000"
      - phone_number: "+0987654321"
        contact_info:
          name: "John Smith"
          company: "American Inc"
          title: "CTO"
        preferences:
          language: "en"
          timezone: "America/New_York"
        metadata:
          priority: "medium"
          customer_type: "customer"
          tags:
            - "english"
            - "tech-focused"
    output: "advanced_batch"
    transition: "confirm_creation"
    
  confirm_creation:
    state_type: "command"
    action:
      eval: "print(f'Batch avanzato creato: {advanced_batch.data.name}. ID: {advanced_batch.batch_id}')"
    transition: "end"
    
  end:
    state_type: "end"
```

### Esempio 3: Lista e Monitoraggio

```yaml
variables:
  ELEVENLABS_API_KEY: "your_api_key_here"
  
states:
  list_all_batches:
    state_type: "elevenlabs_batch_calling"
    operation: "list"
    api_key: "{ELEVENLABS_API_KEY}"
    limit: 10
    output: "batch_list"
    transition: "process_list"
    
  process_list:
    state_type: "command"
    action:
      eval: |
        print(f"Trovati {batch_list.batch_count} batch calls:")
        for batch in batch_list.data.batch_calls:
            print(f"- {batch['name']} (ID: {batch['id']}) - Status: {batch['status']}")
    transition: "end"
    
  end:
    state_type: "end"
```

### Esempio 4: Batch Call Programmato con Variabili

```yaml
variables:
  ELEVENLABS_API_KEY: "your_api_key_here"
  SCHEDULED_TIME: 1735689600  # 1 gennaio 2025, 00:00:00 UTC
  CUSTOMER_NAME: "Maria Garcia"
  CUSTOMER_PHONE: "+34987654321"
  CUSTOMER_LANG: "es"
  
states:
  schedule_batch_call:
    state_type: "elevenlabs_batch_calling"
    operation: "submit"
    api_key: "{ELEVENLABS_API_KEY}"
    call_name: "New Year Greetings 2025"
    agent_id: "your-agent-id" 
    agent_phone_number_id: "your-phone-number-id"
    recipients: '[{"phone_number": "{CUSTOMER_PHONE}", "name": "{CUSTOMER_NAME}", "language": "{CUSTOMER_LANG}", "custom_data": "Holiday Greetings"}]'
    scheduled_time_unix: "{SCHEDULED_TIME}"
    output: "scheduled_batch"
    transition: "confirm_scheduling"
    
  confirm_scheduling:
    state_type: "command"
    action:
      eval: "print(f'Batch call programmato per {scheduled_batch.data.name}. ID: {scheduled_batch.batch_id}')"
    transition: "end"
    
  end:
    state_type: "end"
```

### Esempio 5: Workflow Completo con Loop di Monitoraggio

```yaml
variables:
  ELEVENLABS_API_KEY: "your_api_key_here"
  monitoring_active: true
  
states:
  create_campaign:
    state_type: "elevenlabs_batch_calling"
    operation: "submit"
    api_key: "{ELEVENLABS_API_KEY}"
    call_name: "Customer Survey Campaign"
    agent_id: "your-agent-id"
    agent_phone_number_id: "your-phone-number-id"
    recipients:
      - phone_number: "+1234567890"
        contact_info:
          name: "Cliente A"
      - phone_number: "+0987654321"
        contact_info:
          name: "Cliente B"
    output: "campaign_result"
    success_transition: "start_monitoring"
    error_transition: "campaign_failed"
    
  start_monitoring:
    state_type: "command"
    action:
      eval: "print(f'Campaign creata: {campaign_result.batch_id}. Inizio monitoraggio...')"
    transition: "monitor_loop"
    
  monitor_loop:
    state_type: "if"
    condition: "{monitoring_active} == True"
    true_transition: "check_status"
    false_transition: "end"
    
  check_status:
    state_type: "elevenlabs_batch_calling"
    operation: "get"
    api_key: "{ELEVENLABS_API_KEY}"
    batch_id: "{campaign_result.batch_id}"
    output: "current_status"
    transition: "evaluate_status"
    
  evaluate_status:
    state_type: "switch"
    variable: "{current_status.data.status}"
    cases:
      "completed":
        transition: "campaign_completed"
      "failed":
        transition: "campaign_failed"
      "cancelled":
        transition: "campaign_cancelled"
    default_transition: "wait_and_continue"
    
  wait_and_continue:
    state_type: "command"
    action:
      eval: |
        import time
        print(f"Status: {current_status.data.status} - Chiamate completate: {current_status.data.total_calls_dispatched}/{current_status.data.total_calls_scheduled}")
        time.sleep(30)  # Attendi 30 secondi
    transition: "monitor_loop"
    
  campaign_completed:
    state_type: "command"
    action:
      eval: "print('🎉 Campaign completata con successo!')"
    transition: "end"
    
  campaign_failed:
    state_type: "command"
    action:
      eval: "print('❌ Campaign fallita')"
    transition: "end"
    
  campaign_cancelled:
    state_type: "command" 
    action:
      eval: "print('⚠️ Campaign cancellata')"
    transition: "end"
    
  end:
    state_type: "end"
```

## Formato dei Risultati

### Submit Operation

```json
{
  "success": true,
  "operation": "submit",
  "timestamp": "2025-01-15T10:30:00.123456",
  "batch_id": "batch_12345",
  "status": "pending",
  "total_calls_scheduled": 3,
  "message": "Batch call 'Marketing Campaign Q1' creato con successo",
  "data": {
    "id": "batch_12345",
    "phone_number_id": "phone_123",
    "name": "Marketing Campaign Q1",
    "agent_id": "agent_456",
    "created_at_unix": 1641891000,
    "scheduled_time_unix": null,
    "total_calls_dispatched": 0,
    "total_calls_scheduled": 3,
    "last_updated_at_unix": 1641891000,
    "status": "pending",
    "agent_name": "My Agent",
    "phone_provider": "twilio"
  }
}
```

### Get Operation

```json
{
  "success": true,
  "operation": "get",
  "timestamp": "2025-01-15T10:35:00.123456",
  "batch_id": "batch_12345",
  "status": "in_progress",
  "total_calls_dispatched": 1,
  "total_calls_scheduled": 3,
  "message": "Informazioni batch call recuperate",
  "data": {
    "id": "batch_12345",
    "phone_number_id": "phone_123",
    "name": "Marketing Campaign Q1",
    "agent_id": "agent_456",
    "created_at_unix": 1641891000,
    "scheduled_time_unix": null,
    "total_calls_dispatched": 1,
    "total_calls_scheduled": 3,
    "last_updated_at_unix": 1641891300,
    "status": "in_progress",
    "agent_name": "My Agent",
    "phone_provider": "twilio"
  }
}
```

### List Operation

```json
{
  "success": true,
  "operation": "list",
  "timestamp": "2025-01-15T10:40:00.123456",
  "batch_count": 2,
  "has_more": false,
  "next_doc": null,
  "message": "Recuperati 2 batch calls",
  "data": {
    "batch_calls": [
      {
        "id": "batch_12345",
        "phone_number_id": "phone_123",
        "name": "Marketing Campaign Q1",
        "agent_id": "agent_456",
        "created_at_unix": 1641891000,
        "status": "completed",
        "phone_provider": "twilio"
      },
      {
        "id": "batch_67890", 
        "phone_number_id": "phone_123",
        "name": "Customer Survey Campaign",
        "agent_id": "agent_456",
        "created_at_unix": 1641894600,
        "status": "in_progress",
        "phone_provider": "twilio"
      }
    ],
    "next_doc": null,
    "has_more": false
  }
}
```

### Formato Errore

```json
{
  "success": false,
  "operation": "submit",
  "error": "Errore HTTP durante submit: 401 Client Error - Dettagli: {'detail': 'Invalid API key'}",
  "status_code": 401,
  "timestamp": "2025-01-15T10:30:00.123456"
}
```

## Stati delle Chiamate

- **pending**: Il batch è stato creato ma non ancora avviato
- **in_progress**: Le chiamate sono in corso
- **completed**: Tutte le chiamate sono state completate
- **failed**: Il batch è fallito
- **cancelled**: Il batch è stato cancellato

## Gestione degli Errori

Il plugin gestisce diversi tipi di errore:

- **Errori di validazione**: Parametri mancanti o non validi
- **Errori di autenticazione**: API key non valida
- **Errori di connessione**: Problemi di rete
- **Errori API**: Errori restituiti dall'API ElevenLabs

Tutti gli errori vengono loggati dettagliatamente e salvati nella variabile di output se specificata.

## 🎨 Esperienza Frontend

Grazie alla nuova architettura con oggetti annidati, il frontend di IntellyHub può generare automaticamente un'interfaccia utente intuitiva:

### ✨ UI Generata Automaticamente

**Per ogni recipient, il frontend mostra:**
- 📱 **Campo Telefono**: Input validato per numero internazionale
- 👤 **Sezione Contact Info**: Form collassabile con name, company, title, department
- ⚙️ **Sezione Preferences**: Language selector, timezone picker, orari personalizzati
- 📊 **Sezione Metadata**: Priority dropdown, customer type, tag manager, campi custom

### 🔧 Vantaggi UX

1. **➕ Aggiunta Recipients**: Bottone "+" per aggiungere nuovi recipients
2. **🗑️ Rimozione Facile**: Bottone "X" su ogni recipient
3. **📂 Sezioni Collassabili**: Organizzazione pulita delle informazioni
4. **✅ Validazione Real-time**: Controllo immediato dei dati inseriti
5. **🔄 Sostituzione Variabili**: Preview automatica dei valori sostituiti

### 📋 Schema UI nel Manifest

Il manifest include uno schema `ui_schema` che guida il frontend:

```json
"ui_schema": {
  "recipients": {
    "ui_component": "array_builder",
    "item_template": {
      "phone_number": {
        "ui_component": "text_input",
        "validation": "phone"
      },
      "contact_info": {
        "ui_component": "collapsible_section",
        "title": "Informazioni Contatto"
      },
      "preferences": {
        "ui_component": "collapsible_section", 
        "title": "Preferenze Comunicazione"
      },
      "metadata": {
        "ui_component": "collapsible_section",
        "title": "Metadati",
        "advanced": true
      }
    }
  }
}
```

## Best Practices

1. **Usa variabili d'ambiente** per l'API key invece di hardcodarla
2. **Implementa gestione errori** usando `error_transition`
3. **Monitora lo stato** dei batch call usando operazione "get"
4. **Utilizza la paginazione** per liste grandi con il parametro `last_doc`
5. **Programma chiamate** per ottimizzare i tempi di contatto
6. **Logga risultati** per debugging e monitoraggio

## Supporto

Per problemi o domande:
- Controlla i log di IntellyHub per errori dettagliati
- Verifica la configurazione dell'agent ElevenLabs
- Assicurati che l'API key abbia i permessi necessari
- Consulta la documentazione ufficiale ElevenLabs

## Links Utili

- [ElevenLabs Conversational AI](https://elevenlabs.io/docs/conversational-ai)
- [ElevenLabs Batch Calling API](https://elevenlabs.io/docs/api-reference/batch-calling/create)
- [IntellyHub Plugin System](../../../documentazione/PLUGIN_SYSTEM.md)