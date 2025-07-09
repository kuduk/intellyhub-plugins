import logging
import feedparser
import hashlib
from datetime import datetime, timedelta
from .base_state import BaseState

logger = logging.getLogger(__name__)

class RSSArticle:
    """
    Classe che rappresenta un singolo articolo RSS.
    Fornisce un'interfaccia pulita per accedere ai dati dell'articolo.
    """
    def __init__(self, data):
        self._data = data
    
    @property
    def id(self):
        return self._data.get('id', '')
    
    @property
    def title(self):
        return self._data.get('title', '')
    
    @property
    def link(self):
        return self._data.get('link', '')
    
    @property
    def description(self):
        return self._data.get('description', '')
    
    @property
    def author(self):
        return self._data.get('author', '')
    
    @property
    def published(self):
        return self._data.get('published')
    
    @property
    def published_datetime(self):
        """Restituisce la data di pubblicazione come oggetto datetime"""
        if self.published:
            try:
                return datetime.fromisoformat(self.published.replace('Z', '+00:00'))
            except:
                return None
        return None
    
    @property
    def tags(self):
        return self._data.get('tags', [])
    
    @property
    def feed_title(self):
        return self._data.get('feed_title', '')
    
    @property
    def feed_url(self):
        return self._data.get('feed_url', '')
    
    def to_dict(self):
        """Restituisce i dati come dizionario"""
        return self._data.copy()
    
    def __str__(self):
        return f"RSSArticle(title='{self.title}', published='{self.published}')"
    
    def __repr__(self):
        return self.__str__()

class RSSFeedResult:
    """
    Classe che rappresenta il risultato completo della lettura di un feed RSS.
    Fornisce metodi di utilità per filtrare e processare gli articoli.
    """
    def __init__(self, feed_info, articles_data, stats):
        self.feed_info = feed_info
        self.stats = stats
        self._articles = [RSSArticle(article_data) for article_data in articles_data]
    
    @property
    def articles(self):
        """Lista di oggetti RSSArticle"""
        return self._articles
    
    @property
    def feed_title(self):
        return self.feed_info.get('feed_title', '')
    
    @property
    def feed_url(self):
        return self.feed_info.get('feed_url', '')
    
    @property
    def feed_description(self):
        return self.feed_info.get('feed_description', '')
    
    @property
    def total_articles(self):
        return len(self._articles)
    
    @property
    def lookback_hours(self):
        return self.stats.get('lookback_hours', 0)
    
    def get_articles_by_author(self, author):
        """Filtra gli articoli per autore"""
        return [article for article in self._articles if article.author.lower() == author.lower()]
    
    def get_articles_with_tag(self, tag):
        """Filtra gli articoli che contengono un tag specifico"""
        return [article for article in self._articles if tag.lower() in [t.lower() for t in article.tags]]
    
    def get_articles_since(self, hours_ago):
        """Filtra gli articoli pubblicati nelle ultime N ore"""
        cutoff = datetime.now() - timedelta(hours=hours_ago)
        return [article for article in self._articles 
                if article.published_datetime and article.published_datetime > cutoff]
    
    def search_articles(self, keyword):
        """Cerca articoli che contengono una parola chiave nel titolo o descrizione"""
        keyword = keyword.lower()
        return [article for article in self._articles 
                if keyword in article.title.lower() or keyword in article.description.lower()]
    
    def to_dict(self):
        """Restituisce tutti i dati come dizionario (per compatibilità)"""
        return {
            "feed_info": self.feed_info,
            "articles": [article.to_dict() for article in self._articles],
            "stats": self.stats
        }
    
    def __len__(self):
        return len(self._articles)
    
    def __iter__(self):
        return iter(self._articles)
    
    def __getitem__(self, index):
        return self._articles[index]
    
    def __str__(self):
        return f"RSSFeedResult(feed='{self.feed_title}', articles={len(self._articles)})"
    
    def __repr__(self):
        return self.__str__()

class RSSReaderState(BaseState):
    """
    Stato per leggere un feed RSS e filtrare gli articoli per data.
    
    Parametri di configurazione:
    - feed_url: URL del feed RSS da leggere (obbligatorio)
    - lookback_hours: Numero di ore da guardare indietro (default: 24)
    - max_entries: Numero massimo di articoli da processare (default: 50)
    - output_variable: Nome della variabile dove salvare i risultati (default: "rss_articles")
    - transition: Stato successivo
    """
    
    state_type = "rss_reader"
    
    def execute(self, variables):
        try:
            # Ottieni i parametri di configurazione
            feed_url = self.format_recursive(self.state_config.get("feed_url"), variables)
            lookback_hours = int(self.format_recursive(str(self.state_config.get("lookback_hours", 24)), variables))
            max_entries = int(self.format_recursive(str(self.state_config.get("max_entries", 50)), variables))
            output_variable = self.format_recursive(self.state_config.get("output_variable", "rss_articles"), variables)
            
            # Validazione parametri
            if not feed_url:
                raise ValueError("Il parametro 'feed_url' è obbligatorio per rss_reader")
            
            logger.info(f"🔍 Lettura feed RSS: {feed_url}")
            logger.info(f"⏰ Lookback: {lookback_hours} ore, Max entries: {max_entries}")
            
            # Calcola la data limite per il filtro
            cutoff_date = datetime.now() - timedelta(hours=lookback_hours)
            
            # Leggi e analizza il feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"⚠️  Feed potenzialmente malformato: {feed_url}")
            
            # Informazioni sul feed
            feed_info = {
                "feed_title": feed.feed.get('title', ''),
                "feed_description": feed.feed.get('description', ''),
                "feed_url": feed_url,
                "feed_last_updated": feed.feed.get('updated', ''),
                "total_entries": len(feed.entries)
            }
            
            # Processa gli articoli
            filtered_articles = []
            processed_count = 0
            
            for entry in feed.entries[:max_entries]:
                processed_count += 1
                
                # Estrai la data di pubblicazione
                published_date = self._extract_published_date(entry)
                
                # Filtra per data se disponibile
                if published_date and published_date < cutoff_date:
                    logger.debug(f"⏭️  Articolo troppo vecchio: {entry.get('title', 'N/A')}")
                    continue
                
                # Estrai i dati dell'articolo
                article_data = self._extract_article_data(entry, feed_info, published_date)
                filtered_articles.append(article_data)
            
            # Statistiche
            stats = {
                "total_processed": processed_count,
                "filtered_count": len(filtered_articles),
                "lookback_hours": lookback_hours,
                "cutoff_date": cutoff_date.isoformat()
            }
            
            # Crea l'oggetto risultato strutturato
            result = RSSFeedResult(feed_info, filtered_articles, stats)
            
            # Salva il risultato nella variabile specificata
            variables[output_variable] = result
            
            logger.info(f"✅ Feed RSS processato: {len(filtered_articles)} articoli trovati (su {processed_count} processati)")
            
            return self.state_config.get("transition")
            
        except Exception as e:
            logger.error(f"❌ Errore nella lettura del feed RSS: {e}")
            
            # In caso di errore, salva informazioni sull'errore
            error_result = {
                "error": str(e),
                "feed_url": feed_url if 'feed_url' in locals() else None,
                "articles": [],
                "stats": {
                    "total_processed": 0,
                    "filtered_count": 0,
                    "error": True
                }
            }
            
            variables[output_variable if 'output_variable' in locals() else "rss_articles"] = error_result
            
            # Continua al prossimo stato anche in caso di errore
            return self.state_config.get("transition")
    
    def _extract_published_date(self, entry):
        """
        Estrae la data di pubblicazione da un entry RSS.
        """
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6])
            else:
                return None
        except Exception:
            return None
    
    def _extract_article_data(self, entry, feed_info, published_date):
        """
        Estrae i dati rilevanti da un articolo RSS.
        """
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
        
        # ID univoco dell'articolo
        article_id = self._generate_article_id(entry)
        
        return {
            "id": article_id,
            "title": entry.get('title', ''),
            "link": entry.get('link', ''),
            "description": description,
            "author": author,
            "published": published_date.isoformat() if published_date else None,
            "tags": tags,
            "feed_title": feed_info["feed_title"],
            "feed_url": feed_info["feed_url"]
        }
    
    def _generate_article_id(self, entry):
        """
        Genera un ID univoco per un articolo basato su link e titolo.
        """
        unique_string = f"{entry.get('link', '')}{entry.get('title', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
