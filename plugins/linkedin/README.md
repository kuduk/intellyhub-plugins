# 🔗 LinkedIn Plugin v1.0.0

Plugin avanzato per estrarre dati pubblici da LinkedIn tramite web scraping. Supporta ricerca di profili persone e aziende con filtri configurabili e integrazione LLM opzionale per analisi intelligente dei dati.

## ✨ Caratteristiche

- ✅ **Ricerca Profili Persone** - Estrazione dati da profili pubblici
- ✅ **Ricerca Aziende** - Informazioni su aziende e organizzazioni
- ✅ **Filtri Avanzati** - Posizione, settore, dimensioni azienda, livello esperienza
- ✅ **Doppia Modalità Scraping** - Requests/BeautifulSoup e Selenium
- ✅ **Integrazione LLM** - Analisi intelligente con LangChain
- ✅ **Anti-Detection** - Headers realistici e user-agent rotation
- ✅ **Gestione Errori Robusta** - Fallback e retry automatici
- ✅ **Output Strutturato** - Dati JSON ben organizzati

## 🚀 Installazione

### Metodo 1: Package Manager (Raccomandato)

Aggiungi al tuo `plugins.yaml`:

```yaml
dependencies:
  - linkedin>=1.0.0
```

Installa:
```bash
python -m package_manager install
```

### Metodo 2: Installazione Manuale

1. Copia la directory `linkedin/` in `intellyhub-plugins/plugins/`
2. Installa le dipendenze:
```bash
pip install requests beautifulsoup4 selenium langchain fake-useragent
```

## 📋 Configurazione

### Parametri Base

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|--------------|-------------|
| `search_type` | string | ✅ | Tipo ricerca: `people` o `companies` |
| `search_query` | string | ✅ | Query di ricerca (es. "Software Engineer") |
| `max_results` | integer | ❌ | Numero massimo risultati (default: 10) |
| `output` | string | ❌ | Variabile per salvare i risultati |

### Filtri Disponibili

```yaml
filters:
  location: "Milano, Italia"           # Posizione geografica
  industry: "Technology"               # Settore industriale
  company_size: "51-200"              # Dimensioni azienda
  experience_level: "mid"             # Livello esperienza (entry/mid/senior)
```

### Opzioni Selenium

```yaml
use_selenium: true
selenium_options:
  headless: true                      # Modalità headless (default: true)
  wait_time: 5                        # Tempo attesa in secondi (default: 3)
```

### Integrazione LLM

```yaml
llm_analysis:
  enabled: true
  provider: "openai"                  # openai, ollama, anthropic
  model: "gpt-3.5-turbo"
  api_key: "{openai_key}"
  analysis_type: "summary"            # summary, classification, insights
  custom_prompt: "Analizza questi profili..." # Prompt personalizzato
```

## 💡 Esempi di Utilizzo

### Esempio 1: Ricerca Base Profili

```yaml
states:
  search_developers:
    state_type: "linkedin"
    search_type: "people"
    search_query: "Software Engineer"
    max_results: 20
    output: "developers"
    transition: "process_results"
```

### Esempio 2: Ricerca Aziende con Filtri

```yaml
states:
  search_tech_companies:
    state_type: "linkedin"
    search_type: "companies"
    search_query: "Technology"
    filters:
      location: "Italia"
      company_size: "51-200"
      industry: "Information Technology"
    max_results: 15
    output: "tech_companies"
    success_transition: "analyze_companies"
    error_transition: "handle_error"
```

### Esempio 3: Ricerca con Analisi LLM

```yaml
variables:
  openai_key: "sk-your-api-key"

states:
  search_and_analyze:
    state_type: "linkedin"
    search_type: "people"
    search_query: "Data Scientist"
    filters:
      location: "Milano, Italia"
      experience_level: "senior"
    max_results: 10
    llm_analysis:
      enabled: true
      provider: "openai"
      model: "gpt-3.5-turbo"
      api_key: "{openai_key}"
      analysis_type: "insights"
    output: "data_scientists_analysis"
    transition: "next_step"
```

### Esempio 4: Ricerca Avanzata con Selenium

```yaml
states:
  advanced_search:
    state_type: "linkedin"
    search_type: "people"
    search_query: "Product Manager"
    use_selenium: true
    selenium_options:
      headless: true
      wait_time: 5
    filters:
      location: "Roma, Italia"
      industry: "Technology"
    max_results: 25
    output: "product_managers"
    transition: "process_data"
```

### Esempio 5: Ricerca Geografica Avanzata

```yaml
# Ricerca con geografia nella query + filtro location
states:
  search_milan_startups:
    state_type: "linkedin"
    search_type: "people"
    search_query: "Founder startup Milano"  # Geografia nella query
    filters:
      location: "Lombardia, Italia"        # Filtro regionale
      experience_level: "senior"
    max_results: 30
    output: "milan_founders"
    transition: "analyze_ecosystem"
```

### Esempio 6: Ricerca Multi-Città

```yaml
# Workflow per cercare in multiple città
variables:
  cities: ["Milano", "Roma", "Torino", "Napoli"]
  current_city_index: 0

states:
  search_current_city:
    state_type: "linkedin"
    search_type: "people"
    search_query: "UX Designer"
    filters:
      location: "{cities[current_city_index]}, Italia"
      experience_level: "mid"
    max_results: 15
    output: "city_results"
    transition: "process_city_results"

  process_city_results:
    state_type: "command"
    action:
      eval: |
        # Aggiungi risultati alla lista globale
        if 'all_designers' not in locals():
            all_designers = []
        all_designers.extend(city_results['results'])
        current_city_index += 1
    transition: "check_more_cities"

  check_more_cities:
    state_type: "if"
    condition: "current_city_index < len(cities)"
    true_transition: "search_current_city"
    false_transition: "final_analysis"
```

### Esempio 7: Ricerca con Fallback Automatico

```yaml
states:
  primary_search:
    state_type: "linkedin"
    search_type: "companies"
    search_query: "Fintech"
    filters:
      location: "Milano, Italia"
      company_size: "11-50"
    use_selenium: true
    selenium_options:
      headless: true
      wait_time: 8
    max_results: 20
    output: "fintech_companies"
    success_transition: "analyze_results"
    error_transition: "fallback_search"

  fallback_search:
    state_type: "linkedin"
    search_type: "companies"
    search_query: "Financial Technology Milano"  # Query più specifica
    filters:
      location: "Italia"  # Area più ampia
    use_selenium: false  # Modalità più semplice
    max_results: 10
    output: "fintech_companies_fallback"
    success_transition: "analyze_fallback"
    error_transition: "manual_intervention"
```

### Esempio 8: Analisi LLM Personalizzata

```yaml
variables:
  openai_key: "sk-your-key"
  analysis_focus: "market_opportunities"

states:
  search_ai_companies:
    state_type: "linkedin"
    search_type: "companies"
    search_query: "Artificial Intelligence"
    filters:
      location: "Italia"
      company_size: "51-200"
    max_results: 25
    llm_analysis:
      enabled: true
      provider: "openai"
      model: "gpt-4"
      api_key: "{openai_key}"
      analysis_type: "insights"
      custom_prompt: |
        Analizza queste aziende AI italiane e fornisci:
        1. Segmentazione per settore di applicazione
        2. Livello di maturità tecnologica
        3. Opportunità di partnership
        4. Trend emergenti nel mercato italiano
        5. Raccomandazioni per investitori
        
        Focus particolare su: {analysis_focus}
    output: "ai_market_analysis"
    transition: "generate_report"
```

### Esempio 9: Ricerca Competenze Specifiche

```yaml
states:
  search_blockchain_experts:
    state_type: "linkedin"
    search_type: "people"
    search_query: "Blockchain Developer Solidity"
    filters:
      location: "Europa"
      experience_level: "senior"
      industry: "Technology"
    max_results: 40
    llm_analysis:
      enabled: true
      provider: "openai"
      model: "gpt-3.5-turbo"
      api_key: "{openai_key}"
      analysis_type: "classification"
      custom_prompt: |
        Classifica questi esperti blockchain per:
        1. Specializzazione tecnica (DeFi, NFT, Enterprise, etc.)
        2. Livello di seniority
        3. Settore di provenienza
        4. Disponibilità geografica
        Identifica i top 10 profili più interessanti.
    output: "blockchain_talent_pool"
    transition: "talent_mapping"
```

### Esempio 10: Monitoraggio Competitor

```yaml
# Workflow per monitorare assunzioni competitor
variables:
  competitor_companies: ["TechCorp", "InnovateSrl", "DigitalSolutions"]
  monitoring_roles: ["Software Engineer", "Product Manager", "Data Scientist"]

states:
  monitor_competitor_hiring:
    state_type: "linkedin"
    search_type: "people"
    search_query: "{monitoring_roles[0]} {competitor_companies[0]}"
    filters:
      location: "Italia"
    max_results: 20
    llm_analysis:
      enabled: true
      provider: "openai"
      model: "gpt-3.5-turbo"
      api_key: "{openai_key}"
      analysis_type: "summary"
      custom_prompt: |
        Analizza questi profili per identificare:
        1. Nuove assunzioni recenti (ultimi 3 mesi)
        2. Competenze chiave richieste
        3. Livelli di seniority
        4. Trend di crescita del team
        5. Possibili strategie di recruiting
    output: "competitor_analysis"
    transition: "save_intelligence"
```

## 📊 Struttura Output

### Dati Base per Profili Persone

```json
{
  "search_type": "people",
  "search_query": "Software Engineer",
  "results_count": 10,
  "results": [
    {
      "name": "Mario Rossi",
      "title": "Senior Software Engineer",
      "location": "Milano, Italia",
      "profile_url": "https://linkedin.com/in/mario-rossi",
      "image_url": "https://media.licdn.com/...",
      "extracted_at": "2024-01-15T10:30:00"
    }
  ],
  "llm_analysis": {
    "analysis": "Analisi dettagliata...",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "analysis_type": "summary"
  },
  "extracted_at": "2024-01-15T10:30:00",
  "success": true
}
```

### Dati Base per Aziende

```json
{
  "search_type": "companies",
  "search_query": "Technology",
  "results_count": 5,
  "results": [
    {
      "name": "TechCorp Italia",
      "title": "Software Development Company",
      "location": "Milano, Italia",
      "profile_url": "https://linkedin.com/company/techcorp",
      "image_url": "https://media.licdn.com/...",
      "extracted_at": "2024-01-15T10:30:00"
    }
  ],
  "success": true
}
```

## 🔧 Tipi di Analisi LLM

### 1. Summary (Riassunto)
Genera un riassunto dettagliato dei risultati con:
- Numero totale risultati
- Tendenze principali
- Competenze/settori più comuni
- Distribuzione geografica
- Insights interessanti

### 2. Classification (Classificazione)
Classifica i profili/aziende in categorie con:
- Categorie identificate
- Numero elementi per categoria
- Caratteristiche distintive

### 3. Insights (Approfondimenti)
Genera insights strategici con:
- Opportunità di business
- Trend del mercato
- Raccomandazioni strategiche
- Potenziali contatti chiave

## ⚙️ Configurazioni Avanzate

### Workflow Completo con Post-Processing

```yaml
listener:
  type: "webhook"
  port: 8080

variables:
  openai_key: "sk-your-key"
  search_location: "Milano, Italia"

states:
  search_profiles:
    state_type: "linkedin"
    search_type: "people"
    search_query: "{job_title}"
    filters:
      location: "{search_location}"
      experience_level: "mid"
    max_results: 20
    llm_analysis:
      enabled: true
      provider: "openai"
      api_key: "{openai_key}"
      analysis_type: "classification"
    output: "linkedin_results"
    success_transition: "save_results"
    error_transition: "handle_error"

  save_results:
    state_type: "file"
    action: "write"
    path: "results/linkedin_search_{timestamp}.json"
    content: "{linkedin_results}"
    transition: "send_notification"

  send_notification:
    state_type: "command"
    action:
      eval: "print(f'✅ Trovati {linkedin_results.results_count} profili')"
    transition: "end"

  handle_error:
    state_type: "command"
    action:
      eval: "print(f'❌ Errore: {linkedin_results.error}')"
    transition: "end"

  end:
    state_type: "end"
```

## 🛡️ Limitazioni e Considerazioni

### Rate Limiting
- LinkedIn implementa rate limiting aggressivo
- Usa pause tra le richieste (implementate automaticamente)
- Considera l'uso di proxy per volumi elevati

### Contenuto Pubblico
- Estrae solo dati pubblicamente visibili
- Alcuni profili potrebbero essere limitati
- Rispetta i termini di servizio di LinkedIn

### Anti-Detection
- User-agent rotation automatica
- Headers realistici
- Supporto Selenium per contenuti dinamici

## 🔍 Troubleshooting

### Problema: Nessun risultato trovato
```yaml
# Soluzione: Usa Selenium per contenuti dinamici
use_selenium: true
selenium_options:
  headless: false  # Per debug
  wait_time: 10
```

### Problema: Errore "Challenge required"
```yaml
# Soluzione: Cambia user-agent o usa proxy
# LinkedIn ha rilevato attività automatizzata
```

### Problema: Errore LLM
```yaml
# Verifica configurazione LLM
llm_analysis:
  enabled: true
  provider: "openai"
  api_key: "sk-valid-key"  # Verifica validità
```

## 📈 Performance

### Modalità Requests (Veloce)
- ~2-5 secondi per ricerca
- Limitato a contenuti statici
- Minore consumo risorse

### Modalità Selenium (Completa)
- ~10-20 secondi per ricerca
- Accesso a contenuti dinamici
- Maggiore consumo risorse

## 🤝 Contributi

Per contribuire al plugin:

1. Fork del repository
2. Crea branch feature
3. Implementa miglioramenti
4. Test approfonditi
5. Pull request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.

## ⚠️ Disclaimer

Questo plugin è destinato solo per l'estrazione di dati pubblici da LinkedIn. Gli utenti sono responsabili del rispetto dei termini di servizio di LinkedIn e delle leggi applicabili sulla privacy e protezione dei dati.

---

**Sviluppato con ❤️ per la community IntellyHub**
