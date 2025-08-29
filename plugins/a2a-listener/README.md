# A2A Listener Plugin

Plugin listener per comunicazione automation-to-automation. Permette a workflow di triggerare altri workflow in cascata creando catene di automazione complesse.

## Caratteristiche

- ✅ Comunicazione inter-workflow
- ✅ Canali dedicati per messaggi
- ✅ Filtraggio messaggi avanzato
- ✅ Passaggio dati tra automazioni
- ✅ Orchestrazione workflow complessi
- ✅ Event-driven architecture

## Configurazione

### Parametri Obbligatori

- `channel`: Canale A2A su cui ascoltare messaggi

### Parametri Opzionali

- `filter`: Filtro per tipologia di messaggi da processare

## Variabili Iniettate

- `a2a_message`: Messaggio ricevuto dal canale A2A
- `a2a_channel`: Canale da cui proviene il messaggio
- `a2a_timestamp`: Timestamp del messaggio
- `a2a_source`: Workflow sorgente che ha inviato il messaggio

## Esempio di Utilizzo

### Workflow Master (Invia)
```yaml
# master-workflow.yaml
states:
  - name: trigger_child
    type: a2a-send
    channel: processing_queue
    message: |
      {
        "task_id": "12345",
        "data": "processing_data",
        "priority": "high"
      }
```

### Workflow Worker (Riceve)
```yaml
# worker-workflow.yaml
listener:
  type: a2a
  channel: processing_queue
  filter: high_priority

states:
  - name: process_task
    type: command
    command: echo "Processing task $a2a_message from $a2a_source"
```

## Casi d'Uso

### Pipeline di Elaborazione
```yaml
# Stage 1: Data Collection
listener:
  type: a2a
  channel: data_collection

states:
  - name: validate_data
    type: if
    condition: valid_data
  - name: send_to_processing
    type: a2a-send
    channel: data_processing
```

### Orchestrazione Microservizi
```yaml
# Service Orchestrator
listener:
  type: a2a
  channel: orchestration
  
states:
  - name: route_request
    type: switch
    cases:
      user_service: { channel: user_processing }
      order_service: { channel: order_processing }
      payment_service: { channel: payment_processing }
```

### Event Sourcing
```yaml
# Event Listener
listener:
  type: a2a
  channel: domain_events
  
states:
  - name: update_read_model
    type: command
    command: update_view "$a2a_message"
```

## Pattern Architetturali

### Fan-Out Pattern
Un workflow master invia a più worker:
```yaml
states:
  - name: distribute_work
    type: parallel
    branches:
      - a2a-send: { channel: worker_1 }
      - a2a-send: { channel: worker_2 }
      - a2a-send: { channel: worker_3 }
```

### Aggregator Pattern
Workflow che raccoglie risultati:
```yaml
listener:
  type: a2a
  channel: results_channel
  
states:
  - name: aggregate_results
    type: collect
    until: all_results_received
```

### Saga Pattern
Gestione transazioni distribuite:
```yaml
listener:
  type: a2a
  channel: saga_coordinator
  
states:
  - name: execute_saga_step
    type: saga-step
    compensate_on_failure: true
```

## Best Practices

- **Usa canali specifici** per evitare conflitti
- **Documenta messaggi** con schema JSON
- **Gestisci errori** e retry automatici
- **Monitora performance** delle catene
- **Implementa circuit breakers** per resilienza
- **Usa filtering** per routing efficiente

## Debugging

Abilita logging dettagliato per tracciare messaggi:
```yaml
listener:
  type: a2a
  channel: debug_channel
  debug: true
```