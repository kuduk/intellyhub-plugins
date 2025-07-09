import logging
import requests
import json
import time
import re
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .base_state import BaseState

logger = logging.getLogger(__name__)

class LinkedInState(BaseState):
    """
    Stato per estrarre dati pubblici da LinkedIn tramite web scraping.
    Versione aggiornata con migliori strategie anti-detection e fallback.
    """
    state_type = "linkedin"
    
    def __init__(self, name, state_config, global_context):
        super().__init__(name, state_config, global_context)
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        
    def _get_headers(self, mobile=False):
        """Genera headers realistici per evitare il blocco."""
        if mobile:
            # User agent mobile per bypassare alcuni controlli
            user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        else:
            user_agent = self.ua.random
            
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def _try_alternative_search(self, search_query, search_type, max_results):
        """Prova ricerche alternative quando LinkedIn blocca."""
        results = []
        
        try:
            # Strategia 1: Ricerca su Google con site:linkedin.com
            google_query = f"site:linkedin.com/in {search_query}"
            if search_type == "companies":
                google_query = f"site:linkedin.com/company {search_query}"
            
            logger.info(f"Tentativo ricerca alternativa via Google: {google_query}")
            
            google_url = f"https://www.google.com/search?q={quote_plus(google_query)}&num={max_results}"
            
            headers = self._get_headers()
            response = self.session.get(google_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Estrai link LinkedIn dai risultati Google
                for link in soup.find_all('a', href=re.compile(r'linkedin\.com/(in|company)/')):
                    href = link.get('href')
                    if 'linkedin.com' in href and len(results) < max_results:
                        # Estrai informazioni dal link e testo
                        text = link.get_text(strip=True)
                        if text and len(text) > 5:  # Filtra link vuoti
                            result = {
                                'name': text[:100],  # Limita lunghezza
                                'profile_url': href,
                                'title': 'Trovato via Google',
                                'location': 'N/A',
                                'extracted_at': datetime.now().isoformat(),
                                'source': 'google_search'
                            }
                            results.append(result)
                
                logger.info(f"Trovati {len(results)} risultati via Google")
                
        except Exception as e:
            logger.warning(f"Ricerca alternativa via Google fallita: {e}")
        
        # Strategia 2: Ricerca su DuckDuckGo (meno restrittivo)
        if len(results) < max_results:
            try:
                ddg_query = f"site:linkedin.com {search_query}"
                ddg_url = f"https://duckduckgo.com/html/?q={quote_plus(ddg_query)}"
                
                headers = self._get_headers()
                response = self.session.get(ddg_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for link in soup.find_all('a', href=re.compile(r'linkedin\.com')):
                        href = link.get('href')
                        if len(results) < max_results:
                            text = link.get_text(strip=True)
                            if text and 'linkedin.com' in href:
                                result = {
                                    'name': text[:100],
                                    'profile_url': href,
                                    'title': 'Trovato via DuckDuckGo',
                                    'location': 'N/A',
                                    'extracted_at': datetime.now().isoformat(),
                                    'source': 'duckduckgo_search'
                                }
                                results.append(result)
                
                logger.info(f"Totale risultati con DuckDuckGo: {len(results)}")
                
            except Exception as e:
                logger.warning(f"Ricerca alternativa via DuckDuckGo fallita: {e}")
        
        return results
    
    def _build_search_url(self, search_type, search_query, filters):
        """Costruisce l'URL di ricerca LinkedIn."""
        base_url = "https://www.linkedin.com/search/results/"
        
        if search_type == "people":
            base_url += "people/"
        elif search_type == "companies":
            base_url += "companies/"
        else:
            raise ValueError(f"search_type non supportato: {search_type}")
        
        # Parametri di ricerca
        params = {
            "keywords": search_query,
            "origin": "GLOBAL_SEARCH_HEADER"
        }
        
        # Applica filtri se presenti
        if filters:
            if filters.get("location"):
                params["geoUrn"] = f"[{quote_plus(filters['location'])}]"
            
            if search_type == "people":
                if filters.get("experience_level"):
                    exp_map = {
                        "entry": "1",
                        "mid": "2,3,4",
                        "senior": "5,6,7,8,9,10"
                    }
                    if filters["experience_level"] in exp_map:
                        params["experience"] = exp_map[filters["experience_level"]]
                
                if filters.get("industry"):
                    params["industry"] = quote_plus(filters["industry"])
            
            elif search_type == "companies":
                if filters.get("company_size"):
                    size_map = {
                        "1-10": "A",
                        "11-50": "B", 
                        "51-200": "C",
                        "201-500": "D",
                        "501-1000": "E",
                        "1001-5000": "F",
                        "5001-10000": "G",
                        "10001+": "H"
                    }
                    if filters["company_size"] in size_map:
                        params["companySize"] = size_map[filters["company_size"]]
                
                if filters.get("industry"):
                    params["companyIndustry"] = quote_plus(filters["industry"])
        
        return f"{base_url}?{urlencode(params)}"
    
    def _scrape_with_requests(self, url, max_results, retry_strategies=True):
        """Scraping con requests e BeautifulSoup con multiple strategie."""
        results = []
        
        try:
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=30)
            
            logger.info(f"Status Code: {response.status_code}, Final URL: {response.url}")
            
            # Controlla se LinkedIn ha reindirizzato a login/challenge
            if "challenge" in response.url or "login" in response.url or "uas/login" in response.url:
                logger.warning("LinkedIn ha richiesto login/challenge - risultati limitati")
                return []
            
            if response.status_code != 200:
                logger.warning(f"Status code non OK: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Prova diversi selettori CSS aggiornati
            selectors = [
                'div[class*="entity-result"]',
                'div[class*="search-result"]',
                'div[class*="result-card"]',
                'div[class*="person-result"]',
                'div[class*="people-result"]',
                'div[class*="company-result"]',
                'li[class*="result"]',
                'article[class*="result"]'
            ]
            
            result_items = []
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    result_items = items
                    logger.info(f"Trovati {len(items)} elementi con selettore: {selector}")
                    break
            
            if not result_items:
                logger.warning("Nessun elemento risultato trovato con i selettori CSS")
                return []
            
            for item in result_items[:max_results]:
                try:
                    result_data = self._extract_result_data(item)
                    if result_data:
                        results.append(result_data)
                except Exception as e:
                    logger.warning(f"Errore nell'estrazione dati da elemento: {e}")
                    continue
            
            logger.info(f"Estratti {len(results)} risultati con requests")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore nella richiesta HTTP: {e}")
            return []
        except Exception as e:
            logger.error(f"Errore nel scraping con requests: {e}")
            return []
    
    def _extract_result_data(self, item):
        """Estrae dati da un singolo elemento risultato con selettori aggiornati."""
        try:
            data = {}
            
            # Nome/Titolo - prova diversi selettori
            name_selectors = [
                'span[aria-hidden="true"]',
                'a[class*="app-aware-link"]',
                'h3 a',
                'h4 a',
                '.entity-result__title-text a',
                '.search-result__title a',
                '[data-control-name*="search_srp_result"] a'
            ]
            
            name_elem = None
            for selector in name_selectors:
                name_elem = item.select_one(selector)
                if name_elem:
                    break
            
            if name_elem:
                data['name'] = name_elem.get_text(strip=True)
            
            # Link al profilo - prova diversi selettori
            link_selectors = [
                'a[href*="/in/"]',
                'a[href*="/company/"]',
                'a[data-control-name*="search_srp_result"]'
            ]
            
            link_elem = None
            for selector in link_selectors:
                link_elem = item.select_one(selector)
                if link_elem:
                    break
            
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('/'):
                        href = 'https://www.linkedin.com' + href
                    data['profile_url'] = href
            
            # Posizione/Descrizione - prova diversi selettori
            desc_selectors = [
                '.entity-result__primary-subtitle',
                '.search-result__info .subline-level-1',
                '.entity-result__summary',
                '[data-field="headline"]'
            ]
            
            desc_elem = None
            for selector in desc_selectors:
                desc_elem = item.select_one(selector)
                if desc_elem:
                    break
            
            if desc_elem:
                data['title'] = desc_elem.get_text(strip=True)
            
            # Località - prova diversi selettori
            location_selectors = [
                '.entity-result__secondary-subtitle',
                '.search-result__info .subline-level-2',
                '[data-field="location"]'
            ]
            
            location_elem = None
            for selector in location_selectors:
                location_elem = item.select_one(selector)
                if location_elem:
                    break
            
            if location_elem:
                data['location'] = location_elem.get_text(strip=True)
            
            # Immagine profilo
            img_elem = item.select_one('img')
            if img_elem and img_elem.get('src'):
                data['image_url'] = img_elem.get('src')
            
            # Timestamp estrazione
            data['extracted_at'] = datetime.now().isoformat()
            
            return data if data.get('name') else None
            
        except Exception as e:
            logger.warning(f"Errore nell'estrazione dati: {e}")
            return None
    
    def execute(self, variables):
        logger.debug(f"Esecuzione LinkedIn scraper '{self.name}' con configurazione: {self.state_config}")
        
        try:
            # Parametri obbligatori
            search_type = self.format_recursive(self.state_config.get("search_type"), variables)
            search_query = self.format_recursive(self.state_config.get("search_query"), variables)
            
            if not search_type or search_type not in ["people", "companies"]:
                logger.error("search_type deve essere 'people' o 'companies'")
                return self.state_config.get("error_transition", "end")
            
            if not search_query:
                logger.error("search_query è obbligatorio")
                return self.state_config.get("error_transition", "end")
            
            # Parametri opzionali
            filters = self.state_config.get("filters", {})
            max_results = int(self.state_config.get("max_results", 10))
            use_alternative_search = self.state_config.get("use_alternative_search", True)
            
            # Formatta i filtri
            if filters:
                filters = self.format_recursive(filters, variables)
            
            logger.info(f"Ricerca LinkedIn: {search_type} - '{search_query}' (max: {max_results})")
            
            # Esegui ricerca alternativa direttamente (LinkedIn blocca le ricerche dirette)
            results = []
            
            if use_alternative_search:
                logger.info("Uso ricerche alternative (Google/DuckDuckGo) per bypassare blocchi LinkedIn")
                results = self._try_alternative_search(search_query, search_type, max_results)
            else:
                # Prova ricerca diretta (probabilmente fallirà)
                search_url = self._build_search_url(search_type, search_query, filters)
                logger.info(f"URL di ricerca diretta: {search_url}")
                results = self._scrape_with_requests(search_url, max_results)
                
                # Se fallisce, usa comunque le alternative
                if not results:
                    logger.info("Ricerca diretta fallita, uso ricerche alternative")
                    results = self._try_alternative_search(search_query, search_type, max_results)
            
            if not results:
                logger.warning("Nessun risultato trovato con tutte le strategie")
            else:
                logger.info(f"Trovati {len(results)} risultati totali")
            
            # Prepara output
            output_data = {
                "search_type": search_type,
                "search_query": search_query,
                "filters": filters,
                "results_count": len(results),
                "results": results,
                "extracted_at": datetime.now().isoformat(),
                "success": len(results) > 0,
                "strategies_used": ["alternative_search"] if use_alternative_search else ["direct_search"],
                "note": "Risultati ottenuti tramite ricerche alternative per bypassare blocchi LinkedIn"
            }
            
            # Salva output se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = output_data
            
            logger.info(f"LinkedIn scraping completato: {len(results)} risultati estratti")
            
            return self.state_config.get("success_transition", self.state_config.get("transition"))
            
        except Exception as e:
            error_msg = f"Errore nell'esecuzione LinkedIn scraper: {e}"
            logger.error(error_msg)
            
            # Salva errore nell'output se specificato
            output_key = self.state_config.get("output")
            if output_key:
                variables[output_key] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            return self.state_config.get("error_transition", "end")
