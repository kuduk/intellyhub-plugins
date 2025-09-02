# Google Sheets Plugin per IntellyHub

Plugin per interagire con Google Sheets attraverso le API di Google. Permette di leggere, scrivere, cercare, aggiungere dati e gestire fogli di calcolo all'interno dei workflow di IntellyHub.

## 🚀 Funzionalità

- **Lettura dati**: Legge dati da range specifici o intere colonne
- **Scrittura dati**: Scrive/aggiorna dati in celle specifiche  
- **Ricerca**: Cerca valori all'interno dei fogli
- **Append**: Aggiunge nuove righe alla fine del foglio
- **Pulizia**: Pulisce range di celle specifici
- **Gestione fogli**: Crea nuovi fogli all'interno del documento

## 📋 Prerequisiti

1. **Google Cloud Console Setup**:
   - Creare un progetto su [Google Cloud Console](https://console.cloud.google.com/)
   - Abilitare la **Google Sheets API**
   - Creare un **Service Account**
   - Scaricare le credenziali JSON del service account

2. **Condivisione del foglio**:
   - Condividere il foglio Google Sheets con l'email del service account
   - Assegnare i permessi appropriati (Editor per scrittura, Viewer per lettura)

## ⚙️ Configurazione

### Credenziali

Ci sono tre modi per configurare le credenziali:

#### 1. JSON inline nel workflow
```yaml
google_sheets_state:
  state_type: google_sheets
  credentials_json: "{GOOGLE_SERVICE_ACCOUNT_KEY}"
  # ... altri parametri
```

#### 2. Percorso file
```yaml
google_sheets_state:
  state_type: google_sheets
  credentials_path: "/path/to/credentials.json"
  # ... altri parametri  
```

#### 3. Variabili ambiente
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
# oppure
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
```

## 📖 Utilizzo

### Lettura Dati

```yaml
read_sheet_data:
  state_type: google_sheets
  action: read
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  sheet_name: "Class Data"
  range: "A2:E"
  output: sheet_data
  success_transition: process_data
  error_transition: handle_error
```

### Scrittura Dati

```yaml
write_sheet_data:
  state_type: google_sheets
  action: write
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  range: "A1:C1"
  values: [["Nome", "Email", "Data"]]
  success_transition: data_written
  error_transition: handle_error
```

### Ricerca Dati

```yaml
search_in_sheet:
  state_type: google_sheets
  action: search
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  search_query: "mario@email.com"
  search_column: "B"  # Opzionale: cerca in colonna specifica
  output: search_results
  transition: process_results
```

### Aggiunta Righe

```yaml
append_data:
  state_type: google_sheets
  action: append
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  sheet_name: "Utenti"
  values: [
    ["Mario Rossi", "mario@email.com", "2024-01-01"],
    ["Giulia Verdi", "giulia@email.com", "2024-01-02"]
  ]
  transition: users_added
```

### Pulizia Dati

```yaml
clear_range:
  state_type: google_sheets
  action: clear
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  range: "A1:Z1000"
  transition: data_cleared
```

### Creazione Nuovo Foglio

```yaml
create_new_sheet:
  state_type: google_sheets
  action: create_sheet
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  sheet_name: "Report {current_date}"
  output: new_sheet_info
  transition: sheet_created
```

## 📊 Struttura Output

### Lettura (`action: read`)
```json
{
  "success": true,
  "data": [
    ["Nome", "Email", "Data"],
    ["Mario", "mario@email.com", "2024-01-01"]
  ],
  "range": "'Sheet1'!A1:C2",
  "rows_count": 2,
  "columns_count": 3
}
```

### Scrittura (`action: write`)
```json
{
  "success": true,
  "updated_cells": 6,
  "updated_range": "'Sheet1'!A1:C2",
  "updated_rows": 2,
  "updated_columns": 3
}
```

### Ricerca (`action: search`)
```json
{
  "success": true,
  "matches": [
    {
      "row": 2,
      "column": "B", 
      "value": "mario@email.com",
      "full_row": ["Mario", "mario@email.com", "2024-01-01"]
    }
  ],
  "matches_count": 1,
  "search_query": "mario@email.com",
  "search_column": "B"
}
```

## 🛠️ Parametri Configurazione

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|--------------|-------------|
| `action` | string | ✅ | Azione da eseguire (`read`, `write`, `search`, `append`, `clear`, `create_sheet`) |
| `spreadsheet_id` | string | ✅ | ID del foglio Google (dalla URL) |
| `sheet_name` | string | ❌ | Nome del foglio (default: "Sheet1") |
| `range` | string | ❌ | Range in formato A1 (es: "A1:C10") |
| `values` | array | ❌ | Valori da scrivere/aggiungere |
| `search_query` | string | ❌ | Testo da cercare |
| `search_column` | string | ❌ | Colonna per ricerca specifica |
| `credentials_json` | string | ❌ | JSON credenziali service account |
| `credentials_path` | string | ❌ | Percorso file credenziali |
| `output` | string | ❌ | Nome variabile per risultato |
| `success_transition` | string | ❌ | Stato successivo se successo |
| `error_transition` | string | ❌ | Stato successivo se errore |

## 🔧 Esempi Avanzati

### Workflow Completo di Gestione Utenti

```yaml
name: "Gestione Utenti Google Sheets"
start_state: "read_users"

variables:
  sheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  new_user_email: "nuovo@email.com"

states:
  read_users:
    state_type: google_sheets
    action: read
    spreadsheet_id: "{sheet_id}"
    sheet_name: "Utenti"
    range: "A:C"
    output: current_users
    success_transition: check_user_exists
    error_transition: error_handler

  check_user_exists:
    state_type: google_sheets
    action: search
    spreadsheet_id: "{sheet_id}"
    search_query: "{new_user_email}"
    search_column: "B"
    output: user_search
    success_transition: evaluate_search
    error_transition: error_handler

  evaluate_search:
    state_type: if
    condition: "user_search['matches_count'] == 0"
    true_transition: add_user
    false_transition: user_exists

  add_user:
    state_type: google_sheets
    action: append
    spreadsheet_id: "{sheet_id}"
    sheet_name: "Utenti"
    values: [["Nuovo Utente", "{new_user_email}", "{current_date}"]]
    success_transition: user_added
    error_transition: error_handler

  user_added:
    state_type: command
    action:
      eval: "print(f'✅ Utente {new_user_email} aggiunto con successo')"
    transition: end

  user_exists:
    state_type: command
    action:
      eval: "print(f'⚠️ Utente {new_user_email} già esistente')"
    transition: end

  error_handler:
    state_type: command
    action:
      eval: "print('❌ Errore nel processamento')"
    transition: end

  end:
    state_type: end
```

### Sincronizzazione Dati

```yaml
sync_data:
  state_type: google_sheets
  action: write
  spreadsheet_id: "{sheet_id}"
  range: "A1:E{len(processed_data)+1}"
  values: "{processed_data}"
  log:
    message: "Sincronizzati {len(processed_data)} record su Google Sheets"
    level: "info"
  success_transition: data_synced
  error_transition: sync_failed
```

## 🚨 Gestione Errori

Il plugin gestisce automaticamente diversi tipi di errori:

- **Credenziali non valide**: Errore di autenticazione
- **Foglio non trovato**: Spreadsheet ID o sheet name non valido
- **Permessi insufficienti**: Service account senza permessi
- **Range non valido**: Formato range errato
- **API Limits**: Superamento limiti Google API

Usa sempre `error_transition` per gestire gli errori:

```yaml
sheets_operation:
  state_type: google_sheets
  # ... configurazione ...
  success_transition: success_handler
  error_transition: error_handler
```

## 🔍 Tips & Best Practices

1. **Performance**: Per grandi dataset, usa range specifici invece di leggere tutto il foglio
2. **Batch Operations**: Raggruppa più operazioni quando possibile
3. **Error Handling**: Implementa sempre gestione errori con `error_transition`
4. **Security**: Non mettere credenziali direttamente nel YAML, usa variabili ambiente
5. **Monitoring**: Usa il logging per tracciare le operazioni

## 📝 Logging

Il plugin supporta logging dettagliato:

```yaml
sheets_operation:
  state_type: google_sheets
  action: read
  # ... configurazione ...
  log:
    message: "Lettura completata: {sheet_data.rows_count} righe lette"
    level: "info"
```

## 🤝 Contribuire

Per contribuire al plugin:
1. Fork del repository
2. Crea branch feature
3. Test delle modifiche
4. Pull request con descrizione dettagliata

## 📄 Licenza

Questo plugin è rilasciato sotto licenza MIT.