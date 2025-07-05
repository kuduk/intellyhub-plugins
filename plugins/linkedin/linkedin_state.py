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
    Supporta ricerca di profili persone e aziende con filtri configurabili
    e integrazione LLM opzionale per analisi dei dati.
    """
    state_type = "linkedin"
    
    def __init__(self, name, state_config, global_context):
        super().__init__(name, state_config, global_context)
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        
    def _get_headers(self):
        """Genera headers realistici per evitare il blocco."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _setup_selenium(self, selenium_options):
        """Configura Selenium WebDriver se richiesto."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            
            # Configurazioni di base
            if selenium_options.get("headless", True):
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver configurato con successo")
            
        except ImportError:
            logger.error("Selenium non installato. Installa con: pip install selenium")
            raise ImportError("Selenium è richiesto per use_selenium=true")
        except Exception as e:
            logger.error(f"Errore nella configurazione Selenium: {e}")
            raise
    
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
                # LinkedIn usa codici geografici, per semplicità usiamo il nome
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
    
    def _scrape_with_requests(self, url, max_results):
        """Scraping con requests e BeautifulSoup."""
        try:
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # LinkedIn potrebbe bloccare o richiedere login
            if "challenge" in response.url or "login" in response.url:
                logger.warning("LinkedIn ha richiesto login/challenge - risultati limitati")
                return []
            
            results = []
            
            # Cerca elementi dei risultati (selettori potrebbero cambiare)
            result_items = soup.find_all('div', class_=re.compile(r'entity-result'))
            
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
    
    def _scrape_with_selenium(self, url, max_results, selenium_options):
        """Scraping con Selenium per contenuti dinamici."""
        try:
            wait_time = selenium_options.get("wait_time", 3)
            
            self.driver.get(url)
            time.sleep(wait_time)
            
            # Scroll per caricare più contenuti
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Ottieni il contenuto della pagina
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            results = []
            result_items = soup.find_all('div', class_=re.compile(r'entity-result'))
            
            for item in result_items[:max_results]:
                try:
                    result_data = self._extract_result_data(item)
                    if result_data:
                        results.append(result_data)
                except Exception as e:
                    logger.warning(f"Errore nell'estrazione dati da elemento: {e}")
                    continue
            
            logger.info(f"Estratti {len(results)} risultati con Selenium")
            return results
            
        except Exception as e:
            logger.error(f"Errore nel scraping con Selenium: {e}")
            return []
    
    def _extract_result_data(self, item):
        """Estrae dati da un singolo elemento risultato."""
        try:
            data = {}
            
            # Nome/Titolo
            name_elem = item.find('span', {'aria-hidden': 'true'}) or item.find('a', class_=re.compile(r'app-aware-link'))
            if name_elem:
                data['name'] = name_elem.get_text(strip=True)
            
            # Link al profilo
            link_elem = item.find('a', href=re.compile(r'/in/|/company/'))
            if link_elem:
                href = link_elem.get('href')
                if href.startswith('/'):
                    href = 'https://www.linkedin.com' + href
                data['profile_url'] = href
            
            # Posizione/Descrizione
            desc_elem = item.find('div', class_=re.compile(r'entity-result__primary-subtitle'))
            if desc_elem:
                data['title'] = desc_elem.get_text(strip=True)
            
            # Località
            location_elem = item.find('div', class_=re.compile(r'entity-result__secondary-subtitle'))
            if location_elem:
                data['location'] = location_elem.get_text(strip=True)
            
            # Immagine profilo
            img_elem = item.find('img')
            if img_elem and img_elem.get('src'):
                data['image_url'] = img_elem.get('src')
            
            # Timestamp estrazione
            data['extracted_at'] = datetime.now().isoformat()
            
            return data if data.get('name') else None
            
        except Exception as e:
            logger.warning(f"Errore nell'estrazione dati: {e}")
            return None
    
    def _analyze_with_llm(self, results, llm_config, variables):
        """Analizza i risultati con LLM se configurato."""
        try:
            if not llm_config.get("enabled", False):
                return None
            
            # Importa LangChain
            from langchain.llms import OpenAI, Ollama
            from langchain.chat_models import ChatOpenAI, ChatAnthropic
            from langchain.schema import HumanMessage
            
            provider = llm_config.get("provider", "openai").lower()
            model = llm_config.get("model", "gpt-3.5-turbo")
            api_key = self.format_recursive(llm_config.get("api_key"), variables)
            
            # Inizializza LLM
            if provider == "openai":
                llm = ChatOpenAI(
                    model=model,
                    openai_api_key=api_key,
                    temperature=0.7
                )
            elif provider == "ollama":
                llm = Ollama(
                    model=model,
                    base_url=llm_config.get("base_url", "http://localhost:11434")
                )
            elif provider == "anthropic":
                llm = ChatAnthropic(
                    model=model,
                    anthropic_api_key=api_key
                )
            else:
                logger.error(f"Provider LLM non supportato: {provider}")
                return None
            
            # Prepara i dati per l'analisi
            data_summary = json.dumps(results, indent=2, ensure_ascii=False)
            
            # Determina il prompt basato sul tipo di analisi
            analysis_type = llm_config.get("analysis_type", "summary")
            custom_prompt = llm_config.get("custom_prompt")
            
            if custom_prompt:
                prompt = f"{custom_prompt}\n\nDati da analizzare:\n{data_summary}"
            else:
                if analysis_type == "summary":
                    prompt = f"""Analizza i seguenti dati estratti da LinkedIn e fornisci un riassunto dettagliato:

Dati:
{data_summary}

Fornisci:
1. Numero totale di risultati
2. Tendenze principali
3. Competenze/settori più comuni
4. Distribuzione geografica
5. Insights interessanti"""
                
                elif analysis_type == "classification":
                    prompt = f"""Classifica i seguenti profili/aziende LinkedIn in categorie:

Dati:
{data_summary}

Fornisci una classificazione strutturata con:
1. Categorie identificate
2. Numero di elementi per categoria
3. Caratteristiche distintive di ogni categoria"""
                
                elif analysis_type == "insights":
                    prompt = f"""Genera insights strategici dai seguenti dati LinkedIn:

Dati:
{data_summary}

Fornisci:
1. Opportunità di business identificate
2. Trend del mercato
3. Raccomandazioni strategiche
4. Potenziali contatti chiave"""
                
                else:
                    prompt = f"Analizza i seguenti dati LinkedIn:\n{data_summary}"
            
            # Esegui l'analisi
            if hasattr(llm, 'invoke'):
                response = llm.invoke([HumanMessage(content=prompt)])
                analysis = response.content if hasattr(response, 'content') else str(response)
            else:
                analysis = llm(prompt)
            
            logger.info("Analisi LLM completata con successo")
            
            return {
                "analysis": analysis,
                "provider": provider,
                "model": model,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError:
            logger.error("LangChain non installato per analisi LLM")
            return None
        except Exception as e:
            logger.error(f"Errore nell'analisi LLM: {e}")
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
            use_selenium = self.state_config.get("use_selenium", False)
            selenium_options = self.state_config.get("selenium_options", {})
            llm_config = self.state_config.get("llm_analysis", {})
            
            # Formatta i filtri
            if filters:
                filters = self.format_recursive(filters, variables)
            
            # Costruisci URL di ricerca
            search_url = self._build_search_url(search_type, search_query, filters)
            logger.info(f"URL di ricerca: {search_url}")
            
            # Esegui scraping
            results = []
            
            if use_selenium:
                self._setup_selenium(selenium_options)
                results = self._scrape_with_selenium(search_url, max_results, selenium_options)
            else:
                results = self._scrape_with_requests(search_url, max_results)
            
            if not results:
                logger.warning("Nessun risultato trovato")
            
            # Analisi LLM opzionale
            llm_analysis = None
            if llm_config.get("enabled", False) and results:
                llm_analysis = self._analyze_with_llm(results, llm_config, variables)
            
            # Prepara output
            output_data = {
                "search_type": search_type,
                "search_query": search_query,
                "filters": filters,
                "results_count": len(results),
                "results": results,
                "llm_analysis": llm_analysis,
                "extracted_at": datetime.now().isoformat(),
                "success": True
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
        
        finally:
            # Chiudi Selenium se utilizzato
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("Selenium WebDriver chiuso")
                except:
                    pass
