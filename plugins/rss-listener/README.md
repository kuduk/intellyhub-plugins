# RSS Listener Plugin per IntellyHub

Plugin listener per monitorare feed RSS e avviare automaticamente flussi di automazione quando vengono pubblicati nuovi articoli.

## 📡 Caratteristiche

- ✅ **Monitoraggio multipli feed**: Supporta più feed RSS contemporaneamente
- ✅ **Cache intelligente**: Evita di processare articoli già visti
- ✅ **Configurazione flessibile**: Intervallo di controllo e numero massimo di articoli personalizzabili
- ✅ **Estrazione dati completa**: Titolo, descrizione, autore, data, tags, e altro
- ✅ **Gestione errori robusta**: Continua a funzionare anche se un feed è temporaneamente non disponibile
- ✅ **Logging dettagliato**: Traccia tutte le operazioni per debug e monitoraggio

## 📋 Prerequisiti

### Dipendenze Python
Il plugin richiede la libreria `feedparser`:
```bash
pip install feedparser>=6.0.0
```

## 🛠️ Installazione

### Tramite Package Manager (Raccomandato)

1. Aggiungi il plugin al file `plugins.yaml`:
```yaml
dependencies:
  - rss-listener>=1.0.0
```

2. Installa i plugin:
```bash
python -m package_manager install
```

### Installazione Manuale

1. Copia il file `rss_listener.py` nella directory `flow/listeners/`
2. Installa la dipendenza: `pip install feedparser`
3. Riavvia l'applicazione

## ⚙️ Configurazione

### Parametri del Listener

```yaml
listener:
  type: "rsslistener"
  feeds:                    # Lista di URL dei feed RSS (obbligatorio)
    - "https://example.com/feed.xml"
    - "https://another-site.com/rss"
  check_interval: 300       # Intervallo di controllo in secondi (default: 300 = 5 minuti)
  max_entries: 10           # Numero massimo di articoli per feed (default: 10)
```

### Parametri Dettagliati

| Parametro | Tipo | Obbligatorio | Default | Descrizione |
|-----------|------|--------------|---------|-------------|
| `feeds` | Lista/Stringa | ✅ Sì | - | URL dei feed RSS da monitorare |
| `check_interval` | Intero | ❌ No | 300 | Secondi tra i controlli |
| `max_entries` | Intero | ❌ No | 10 | Max articoli per controllo |

## 📊 Variabili Disponibili nel Flusso

Quando viene trovato un nuovo articolo, il listener inietta queste variabili nel flusso:

### Variabili del Feed
- `rss_feed_url` - URL del feed RSS
- `rss_feed_title` - Titolo del feed
- `rss_feed_description` - Descrizione del feed

### Variabili dell'Articolo
- `rss_article_title` - Titolo dell'articolo
- `rss_article_link` - URL dell'articolo
- `rss_article_description` - Descrizione/sommario dell'articolo
- `rss_article_author` - Autore dell'articolo
- `rss_article_published` - Data di pubblicazione (formato ISO)
- `rss_article_tags` - Lista dei tag/categorie
- `rss_article_id` - ID univoco dell'articolo (hash MD5)

## 📖 Esempi di Utilizzo

### Esempio 1: Monitoraggio Semplice

```yaml
# monitor_tech_news.yaml
listener:
  type: "rsslistener"
  feeds:
    - "https://feeds.feedburner.com/oreilly/radar"
  check_interval: 60

states:
  start:
    state_type: "command"
    action:
      eval: "print(f'📰 Nuovo articolo: {rss_article_title}')"
    transition: "end"
    
  end:
    state_type: "end"
```

### Esempio 2: Filtro per Parole Chiave

```yaml
# filter_ai_articles.yaml
listener:
  type: "rsslistener"
  feeds:
    - "https://rss.cnn.com/rss/edition.rss"
    - "https://feeds.bbci.co.uk/news/rss.xml"
  check_interval: 120
  max_entries: 5

states:
  start:
    state_type: "if"
    condition: "'AI' in rss_article_title or 'artificial intelligence' in rss_article_description.lower()"
    true_transition: "process_ai_article"
    false_transition: "end"

  process_ai_article:
    state_type: "command"
    action:
      eval: "print(f'🤖 Articolo AI trovato: {rss_article_title}\\nLink: {rss_article_link}')"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 3: Integrazione con Facebook

```yaml
# rss_to_facebook.yaml
listener:
  type: "rsslistener"
  feeds:
    - "https://feeds.feedburner.com/oreilly/radar"
  check_interval: 300

variables:
  facebook_token: "YOUR_FACEBOOK_TOKEN"
  page_id: "YOUR_PAGE_ID"

states:
  start:
    state_type: "if"
    condition: "'python' in rss_article_title.lower() or 'programming' in rss_article_title.lower()"
    true_transition: "post_to_facebook"
    false_transition: "end"

  post_to_facebook:
    state_type: "facebook"
    access_token: "{facebook_token}"
    page_id: "{page_id}"
    message: "🔥 Articolo interessante: {rss_article_title}\\n\\n{rss_article_description}\\n\\n👉 Leggi di più:"
    link: "{rss_article_link}"
    transition: "end"

  end:
    state_type: "end"
```

### Esempio 4: Salvataggio in File

```yaml
# save_articles.yaml
listener:
  type: "rsslistener"
  feeds:
    - "https://feeds.feedburner.com/oreilly/radar"
  check_interval: 600

states:
  start:
    state_type: "file"
    operation: "append"
    path: "articles.txt"
    content: "[{rss_article_published}] {rss_article_title}\\nAutore: {rss_article_author}\\nLink: {rss_article_link}\\nDescrizione: {rss_article_description}\\n\\n---\\n\\n"
    transition: "end"

  end:
    state_type: "end"
```

## 🔧 Configurazioni Avanzate

### Monitoraggio Multipli Feed con Logica Diversa

```yaml
listener:
  type: "rsslistener"
  feeds:
    - "https://tech-feed.com/rss"
    - "https://news-feed.com/rss"
    - "https://blog-feed.com/rss"
  check_interval: 180
  max_entries: 15

states:
  start:
    state_type: "switch"
    value: "{rss_feed_url}"
    cases:
      "https://tech-feed.com/rss": "process_tech"
      "https://news-feed.com/rss": "process_news"
      "https://blog-feed.com/rss": "process_blog"
    default: "end"

  process_tech:
    state_type: "command"
    action:
      eval: "print(f'💻 Tech: {rss_article_title}')"
    transition: "end"

  process_news:
    state_type: "command"
    action:
      eval: "print(f'📰 News: {rss_article_title}')"
    transition: "end"

  process_blog:
    state_type: "command"
    action:
      eval: "print(f'📝 Blog: {rss_article_title}')"
    transition: "end"

  end:
    state_type: "end"
```

## 🧪 Test e Debug

### Test Base
```bash
python main.py test_rss_simple.yaml
```

### Verifica Caricamento
Il listener dovrebbe apparire nei log di avvio:
```
✅ Listener 'RSSListener' scoperto e registrato con ID: 'rsslistener'
✅ Caricato rss_listener.py: 1 plugin trovati
```

### Debug Logging
Per abilitare logging dettagliato, modifica il livello di log:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## ⚠️ Limitazioni e Considerazioni

### Limitazioni
- **Memoria**: La cache degli articoli processati è mantenuta in memoria
- **Persistenza**: La cache non sopravvive al riavvio dell'applicazione
- **Rate Limiting**: Alcuni feed potrebbero avere limitazioni di accesso

### Best Practices
1. **Intervallo ragionevole**: Non impostare `check_interval` troppo basso (min 30 secondi)
2. **Numero articoli**: Limitare `max_entries` per evitare sovraccarico
3. **Gestione errori**: Implementare sempre transizioni di errore nei flussi
4. **Monitoraggio**: Controllare i log per identificare feed problematici

### Performance
- **Feed multipli**: Ogni feed viene controllato sequenzialmente
- **Timeout**: I feed lenti possono rallentare il controllo generale
- **Memoria**: Ogni articolo processato occupa ~1KB in cache

## 🔍 Risoluzione Problemi

### Errori Comuni

#### 1. Feed Non Accessibile
**Errore**: `❌ Errore nel parsing del feed https://example.com/feed.xml`

**Soluzioni**:
- Verifica che l'URL sia corretto e accessibile
- Controlla la connessione internet
- Alcuni feed potrebbero richiedere User-Agent specifici

#### 2. Listener Non Caricato
**Errore**: Listener non trovato nei log di avvio

**Soluzioni**:
- Verifica che `feedparser` sia installato
- Controlla che il file sia in `flow/listeners/`
- Riavvia l'applicazione

#### 3. Nessun Articolo Processato
**Problema**: Il listener si avvia ma non processa articoli

**Soluzioni**:
- Controlla che il feed abbia articoli recenti
- Verifica il valore di `max_entries`
- Controlla i log per errori di parsing

## 🚀 Casi d'Uso Pratici

1. **Monitoraggio News** - Filtra articoli per parole chiave specifiche
2. **Social Media Automation** - Pubblica automaticamente su Facebook/Twitter
3. **Content Curation** - Salva articoli interessanti in file/database
4. **Notifiche** - Invia email/Slack per articoli specifici
5. **Analytics** - Traccia trends e argomenti popolari
6. **Aggregazione Contenuti** - Combina più feed in un unico flusso

## 📚 Riferimenti

- [Documentazione feedparser](https://feedparser.readthedocs.io/)
- [Specifiche RSS 2.0](https://www.rssboard.org/rss-specification)
- [Specifiche Atom](https://tools.ietf.org/html/rfc4287)
- [IntellyHub Documentation](https://github.com/kuduk/ai-automation-fsm-py)

## 🤝 Supporto

Per problemi o domande:
- Apri un issue su [GitHub](https://github.com/kuduk/intellyhub-plugins)
- Consulta la documentazione completa di IntellyHub

## 📄 Licenza

Questo plugin è distribuito sotto licenza MIT.

---

**Sviluppato per IntellyHub - Sistema di Automazione Intelligente** 🚀
