# RSS Reader Plugin v1.0.0

Plugin avanzato per leggere feed RSS, filtrare articoli per data e fornire un oggetto Python strutturato per l'utilizzo in automatismi.

## 🚀 Caratteristiche

### ✅ Funzionalità Base
- **Lettura RSS universale**: Supporta tutti i formati RSS/Atom standard
- **Filtro temporale**: Configura quante ore guardare indietro (default: 24h)
- **Gestione errori robusta**: Continua l'esecuzione anche con feed malformati
- **Estrazione metadati completa**: Titolo, descrizione, autore, tags, date

### ✅ Oggetto Python Strutturato
- **Classe `RSSFeedResult`**: Oggetto principale con metodi di utilità
- **Classe `RSSArticle`**: Rappresentazione pulita di ogni articolo
- **Interfaccia Pythonic**: Iterabile, indicizzabile, con proprietà intuitive
- **Metodi di filtraggio**: Ricerca, filtro per autore, tag, data

### ✅ Ottimizzato per Automatismi
- **Output strutturato**: Facile da utilizzare in altri stati
- **Filtraggio avanzato**: Cerca per parole chiave, autore, tag
- **Cache intelligente**: Evita duplicati con ID univoci
- **Performance**: Limita articoli processati per efficienza

## 📦 Installazione

### Metodo 1: Package Manager (Raccomandato)

1. Aggiungi al tuo `plugins.yaml`:
```yaml
dependencies:
  - rss-reader>=1.0.0
```

2. Installa:
```bash
python -m package_manager install
```

### Metodo 2: Installazione Manuale

1. Copia il plugin in `flow/states/`
2. Riavvia l'applicazione

## 🔧 Configurazione

### Parametri Obbligatori

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `feed_url` | string | URL del feed RSS da leggere |

### Parametri Opzionali

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `lookback_hours` | integer | 24 | Ore da guardare indietro |
| `max_entries` | integer | 50 | Max articoli da processare |
| `output_variable` | string | "rss_articles" | Nome variabile output |
| `transition` | string | - | Stato successivo |

## 📝 Utilizzo Base

```yaml
states:
  read_news:
    state_type: "rss_reader"
    feed_url: "https://feeds.feedburner.com/oreilly/radar"
    lookback_hours: 24
    max_entries: 20
    output_variable: "tech_news"
    transition: "process_news"

  process_news:
    state_type: "command"
    action:
      eval: |
        print(f"Feed: {tech_news.feed_title}")
        print(f"Articoli: {tech_news.total_articles}")
        
        for article in tech_news.articles[:5]:
            print(f"- {article.title}")
            print(f"  {article.link}")
    transition: "end"
```

## 🎯 Esempi Avanzati

### Filtraggio per Parole Chiave

```yaml
states:
  filter_relevant:
    state_type: "command"
    action:
      eval: |
        # Cerca articoli rilevanti
        keywords = ["AI", "Python", "automation"]
        relevant = []
        
        for keyword in keywords:
            found = rss_data.search_articles(keyword)
            relevant.extend(found)
        
        # Rimuovi duplicati
        unique_articles = []
        seen = set()
        for article in relevant:
            if article.id not in seen:
                seen.add(article.id)
                unique_articles.append(article)
        
        filtered_articles = unique_articles
    transition: "send_notifications"
```

### Integrazione con Altri Plugin

```yaml
states:
  read_and_post:
    state_type: "rss_reader"
    feed_url: "{tech_feed}"
    lookback_hours: 2
    transition: "post_trending"

  post_trending:
    state_type: "facebook"
    access_token: "{fb_token}"
    page_id: "{page_id}"
    message: |
      🔥 Trending: {rss_articles.articles[0].title}
      {rss_articles.articles[0].link}
    transition: "end"
```

## 📊 Struttura Output

### Oggetto RSSFeedResult

```python
# Proprietà principali
result.feed_title          # Titolo del feed
result.feed_url           # URL del feed  
result.feed_description   # Descrizione
result.total_articles     # Numero articoli
result.articles           # Lista RSSArticle

# Metodi di filtraggio
ai_articles = result.search_articles("AI")
author_articles = result.get_articles_by_author("John")
recent = result.get_articles_since(12)  # Ultime 12 ore
tagged = result.get_articles_with_tag("python")

# Utilizzo come lista
for article in result:
    print(article.title)

first_article = result[0]
total_count = len(result)
```

### Oggetto RSSArticle

```python
# Proprietà articolo
article.id                    # ID univoco
article.title                 # Titolo
article.link                  # URL
article.description           # Descrizione
article.author                # Autore
article.published             # Data (ISO string)
article.published_datetime    # Data (datetime object)
article.tags                  # Lista tag
article.feed_title           # Titolo feed origine
```

## 🔄 Workflow Completi

### Monitor News con Notifiche

```yaml
variables:
  news_feeds:
    - "https://feeds.feedburner.com/oreilly/radar"
    - "https://rss.cnn.com/rss/edition.rss"
  alert_keywords: ["AI", "cybersecurity", "breakthrough"]

states:
  monitor_feeds:
    state_type: "loop"
    loop_type: "for"
    items: "{news_feeds}"
    item_var: "current_feed"
    states:
      read_feed:
        state_type: "rss_reader"
        feed_url: "{current_feed}"
        lookback_hours: 6
        output_variable: "feed_data"
        transition: "check_alerts"
      
      check_alerts:
        state_type: "command"
        action:
          eval: |
            alerts = []
            for keyword in alert_keywords:
                found = feed_data.search_articles(keyword)
                alerts.extend(found)
            
            if alerts:
                print(f"🚨 {len(alerts)} alert articles found!")
                alert_articles = alerts
        transition: "send_alerts"
    transition: "summary"
```

### Aggregatore Multi-Feed

```yaml
states:
  aggregate_feeds:
    state_type: "command"
    action:
      eval: |
        all_articles = []
        feeds = [
            "https://feeds.feedburner.com/oreilly/radar",
            "https://rss.cnn.com/rss/edition.rss"
        ]
        
        for feed_url in feeds:
            # Qui useresti un loop per leggere ogni feed
            pass
        
        # Combina e ordina per data
        sorted_articles = sorted(all_articles, 
                               key=lambda x: x.published_datetime or datetime.min, 
                               reverse=True)
    transition: "process_aggregated"
```

## 🛠️ Troubleshooting

### Feed Non Accessibile
```
❌ Errore nella lettura del feed RSS: HTTP Error 404
```
**Soluzione**: Verifica URL, controlla connessione internet

### Nessun Articolo Trovato
```
✅ Feed RSS processato: 0 articoli trovati (su 10 processati)
```
**Soluzione**: Aumenta `lookback_hours` o controlla date nel feed

### Performance Lenta
**Soluzione**: Riduci `max_entries`, usa `lookback_hours` appropriato

## 📈 Metriche e Logging

Il plugin produce log dettagliati:

```
🔍 Lettura feed RSS: https://example.com/feed.xml
⏰ Lookback: 24 ore, Max entries: 50
⚠️  Feed potenzialmente malformato: https://example.com/feed.xml
⏭️  Articolo troppo vecchio: Old Article Title
✅ Feed RSS processato: 15 articoli trovati (su 30 processati)
```

## 🔗 Integrazione

### Con Email Plugin
```yaml
states:
  send_digest:
    state_type: "command"
    action:
      email:
        subject: "Daily Digest"
        body: |
          {% for article in rss_articles.articles[:10] %}
          - {{ article.title }}: {{ article.link }}
          {% endfor %}
```

### Con LLM Agent
```yaml
states:
  analyze_articles:
    state_type: "llm_agent"
    provider: "openai"
    model: "gpt-4"
    prompt: |
      Analizza questi articoli e trova i trend:
      {% for article in rss_articles.articles %}
      - {{ article.title }}: {{ article.description }}
      {% endfor %}
```

## 🚀 Roadmap

- [ ] **v1.1**: Supporto autenticazione HTTP
- [ ] **v1.2**: Cache persistente articoli
- [ ] **v1.3**: Filtri regex avanzati
- [ ] **v1.4**: Supporto feed JSON
- [ ] **v1.5**: Database integration

## 📄 Licenza

MIT License - Vedi file LICENSE per dettagli.

## 🤝 Contributi

1. Fork del repository
2. Crea feature branch
3. Commit delle modifiche
4. Push al branch
5. Crea Pull Request

## 📞 Supporto

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/kuduk/intellyhub-plugins/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/kuduk/intellyhub-plugins/discussions)
- 📖 **Documentazione**: [Plugin Docs](../../documentazione/RSS_READER_PLUGIN_DOCUMENTATION.md)

---

**Sviluppato con ❤️ per IntellyHub Community**
