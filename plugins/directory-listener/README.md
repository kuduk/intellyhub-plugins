# Directory Listener Plugin

Plugin listener per monitorare directory del filesystem. Triggera workflow quando vengono create, modificate o eliminate file in directory specifiche.

## Caratteristiche

- ✅ Monitoring filesystem real-time
- ✅ Supporto eventi multipli (create, modify, delete, move)
- ✅ Filtraggio pattern file avanzato
- ✅ Monitoring ricorsivo directory
- ✅ Performance ottimizzata con watchdog
- ✅ Cross-platform (Linux, macOS, Windows)

## Configurazione

### Parametri Obbligatori

- `path`: Percorso della directory da monitorare

### Parametri Opzionali

- `recursive`: Monitora sottodirectory (default: true)
- `file_patterns`: Array di pattern file da monitorare
- `events`: Tipi di eventi da ascoltare (default: ["created", "modified"])

## Variabili Iniettate

- `file_path`: Percorso completo del file che ha triggerato l'evento
- `file_name`: Nome del file senza percorso
- `event_type`: Tipo di evento (created, modified, deleted, moved)
- `directory`: Directory contenente il file
- `file_size`: Dimensione del file in bytes

## Esempio di Utilizzo

### Monitoraggio Base
```yaml
listener:
  type: directory
  path: /home/user/documents
  recursive: true
  events: ["created", "modified"]

states:
  - name: process_file
    type: command
    command: echo "File $event_type: $file_path"
```

### Elaborazione Documenti
```yaml
listener:
  type: directory
  path: /uploads
  file_patterns: ["*.pdf", "*.docx", "*.txt"]
  events: ["created"]

states:
  - name: extract_text
    type: document-parser
    file: "$file_path"
    
  - name: analyze_content
    type: llm-agent
    model: gpt-4
    prompt: "Analyze this document: $extracted_text"
```

### Backup Automatico
```yaml
listener:
  type: directory
  path: /important/data
  events: ["created", "modified"]

states:
  - name: backup_file
    type: command
    command: cp "$file_path" /backup/$(date +%Y%m%d)_$file_name
```

## Casi d'Uso Avanzati

### Processing Immagini
```yaml
listener:
  type: directory
  path: /photos
  file_patterns: ["*.jpg", "*.png", "*.gif"]
  events: ["created"]

states:
  - name: resize_image
    type: command
    command: convert "$file_path" -resize 800x600 "/processed/$file_name"
    
  - name: extract_metadata
    type: command
    command: exiftool "$file_path"
```

### Log Analysis
```yaml
listener:
  type: directory
  path: /var/log
  file_patterns: ["*.log"]
  events: ["modified"]

states:
  - name: analyze_logs
    type: log-analyzer
    file: "$file_path"
    
  - name: alert_on_errors
    type: if
    condition: errors_found
    then:
      - type: notification
        message: "Errors found in $file_name"
```

### Development Workflow
```yaml
listener:
  type: directory
  path: /project/src
  file_patterns: ["*.py", "*.js", "*.ts"]
  events: ["modified"]

states:
  - name: run_tests
    type: command
    command: pytest tests/
    
  - name: code_quality
    type: command
    command: flake8 "$file_path"
    
  - name: deploy_if_green
    type: if
    condition: tests_passed
    then:
      - type: deployment
        target: staging
```

## Pattern File Supportati

- `*.txt` - Tutti i file .txt
- `*.{jpg,png,gif}` - Multiple estensioni
- `data_*.csv` - Pattern con wildcard
- `report_[0-9]*.pdf` - Pattern con caratteri speciali
- `**/*.py` - Ricorsivo con pattern

## Eventi Supportati

- **created**: File/directory creati
- **modified**: File modificati  
- **deleted**: File/directory eliminati
- **moved**: File/directory spostati

## Performance

### Directory Grandi
```yaml
listener:
  type: directory
  path: /big/directory
  recursive: false  # Migliora performance
  file_patterns: ["*.important"]  # Filtra file specifici
```

### Monitoring Selettivo
```yaml
listener:
  type: directory
  path: /data
  events: ["created"]  # Solo nuovi file
  file_patterns: ["*.json", "*.xml"]  # Solo formati specifici
```

## Esclusioni

Per escludere file temporanei o di sistema:
```yaml
listener:
  type: directory
  path: /project
  file_patterns: 
    - "*.py"
    - "*.js"
    - "!*.pyc"      # Esclude file compilati
    - "!node_modules/*"  # Esclude dipendenze
    - "!.git/*"     # Esclude git
```

## Sicurezza

- **Monitora solo directory necessarie** per performance
- **Usa pattern specifici** per evitare overhead
- **Valida percorsi file** prima dell'elaborazione
- **Implementa rate limiting** per directory molto attive
- **Gestisci permessi** filesystem appropriati

## Debugging

Abilita logging dettagliato:
```yaml
listener:
  type: directory
  path: /debug/path
  debug: true
  log_level: DEBUG
```

## Limitazioni

- **Performance**: Directory con milioni di file possono essere lente
- **Permissions**: Richiede accesso in lettura alle directory
- **Network**: Non supporta filesystem di rete (SMB, NFS)
- **Symbolic Links**: Comportamento può variare per platform