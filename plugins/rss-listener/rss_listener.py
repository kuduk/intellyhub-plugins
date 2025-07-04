import logging
import feedparser
import time
import hashlib
from datetime import datetime
from yaml import safe_load

# Importazioni dal nostro framework
from flow.flow import FlowDiagram
from .base_listener import BaseListener
from flow.utils import SafeLogger

logger = SafeLogger(__name__)

class RSSListener(BaseListener):
    """
    Questo listener monitora uno o più feed RSS, controlla periodicamente
    la presenza di nuovi articoli e, quando ne trova uno, avvia un diagramma
    di flusso passando i dettagli dell'articolo come variabili.
    """
    
    def __init__(self, event_config, global_context=None):
        # Chiama il costruttore della classe base
        super().__init__(event_config, global_context)
        
        # Configurazione del listener
        self.feeds = self.format_recursive(self.event_config.get("feeds", []), self.global_context)
        self.check_interval = int(self.format_recursive(str(self.event_config.get("check_interval", 300)), self.global_context))  # 5 minuti default
        self.max_entries = int(self.format_recursive(str(self.event_config.get("max_entries", 10)), self.global_context))  # Max 10 articoli per controllo
        
        # Validazione configurazione
        if not self.feeds:
            raise ValueError("Configurazione per RSSListener incompleta. 'feeds' è richiesto.")
        
        if isinstance(self.feeds, str):
            self.feeds = [self.feeds]  # Converte stringa singola in lista
        
        # Cache per tracciare gli articoli già processati
        self.processed_articles = set()
        
        logger.info(f"🔧 RSSListener configurato per {len(self.feeds)} feed(s), controllo ogni {self.check_interval} secondi")

    def get_article_id(self, entry):
        """
        Genera un ID univoco per un articolo basato su link e titolo.
        """
        unique_string = f"{entry.get('link', '')}{entry.get('title', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def parse_feed(self, feed_url):
        """
        Analizza un singolo feed RSS e restituisce i nuovi articoli.
        """
        try:
            logger.debug(f"🔍 Controllo feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"⚠️  Feed potenzialmente malformato: {feed_url}")
            
            new_articles = []
            entries = feed.entries[:self.max_entries]  # Limita il numero di articoli
            
            for entry in entries:
                article_id = self.get_article_id(entry)
                
                if article_id not in self.processed_articles:
                    # Estrai i dati dell'articolo
                    article_data = self.extract_article_data(entry, feed, feed_url)
                    new_articles.append(article_data)
                    self.processed_articles.add(article_id)
            
            if new_articles:
                logger.info(f"📰 Trovati {len(new_articles)} nuovi articoli da {feed_url}")
            
            return new_articles
            
        except Exception as e:
            logger.error(f"❌ Errore nel parsing del feed {feed_url}: {e}")
            return []

    def extract_article_data(self, entry, feed, feed_url):
        """
        Estrae i dati rilevanti da un articolo RSS.
        """
        # Data di pubblicazione
        published_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        
        # Descrizione/Sommario
        description = ""
        if hasattr(entry, 'summary'):
            description = entry.summary
        elif hasattr(entry, 'description'):
            description = entry.description
        
        # Autore
        author = ""
        if hasattr(entry, 'author'):
            author = entry.author
        elif hasattr(entry, 'author_detail') and entry.author_detail:
            author = entry.author_detail.get('name', '')
        
        # Tags/Categorie
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags]
        
        return {
            "rss_feed_url": feed_url,
            "rss_feed_title": feed.feed.get('title', ''),
            "rss_feed_description": feed.feed.get('description', ''),
            "rss_article_title": entry.get('title', ''),
            "rss_article_link": entry.get('link', ''),
            "rss_article_description": description,
            "rss_article_author": author,
            "rss_article_published": published_date,
            "rss_article_tags": tags,
            "rss_article_id": self.get_article_id(entry)
        }

    def check_feeds(self):
        """
        Controlla tutti i feed configurati e restituisce i nuovi articoli.
        """
        all_new_articles = []
        
        for feed_url in self.feeds:
            new_articles = self.parse_feed(feed_url)
            all_new_articles.extend(new_articles)
        
        return all_new_articles

    def listen(self, config_file):
        """
        Metodo principale che esegue il polling dei feed RSS
        in un ciclo infinito.
        """
        logger.info(f"▶️  Avvio RSSListener per {len(self.feeds)} feed(s)...")
        
        # Primo controllo per popolare la cache (senza processare)
        logger.info("🔄 Inizializzazione cache articoli esistenti...")
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:self.max_entries]:
                    article_id = self.get_article_id(entry)
                    self.processed_articles.add(article_id)
            except Exception as e:
                logger.error(f"❌ Errore nell'inizializzazione del feed {feed_url}: {e}")
        
        logger.info(f"✅ Cache inizializzata con {len(self.processed_articles)} articoli")
        
        while True:
            try:
                new_articles = self.check_feeds()
                
                for article_data in new_articles:
                    logger.info(f"📰 Nuovo articolo: {article_data['rss_article_title']} da {article_data['rss_feed_title']}")
                    
                    try:
                        # Ricarica la configurazione ad ogni esecuzione
                        with open(config_file, 'r') as f:
                            config = safe_load(f)
                        
                        # Esegui il flow
                        flow = FlowDiagram(config, self.global_context)
                        
                        # Inietta i dati dell'articolo nel contesto del flusso
                        flow.variables.update(article_data)
                        
                        flow.run()
                        
                    except Exception as e:
                        logger.error(f"❌ Errore nell'esecuzione del flow per l'articolo {article_data['rss_article_title']}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"❌ Errore nel ciclo del listener RSS: {e}")
                # In caso di errore, aspetta un po' di più prima di riprovare
                time.sleep(min(self.check_interval * 2, 1800))  # Max 30 minuti
                continue
            
            # Aspetta l'intervallo configurato prima del prossimo controllo
            logger.debug(f"⏰ Prossimo controllo RSS tra {self.check_interval} secondi")
            time.sleep(self.check_interval)
