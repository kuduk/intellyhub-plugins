import time
import os
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from yaml import safe_load
from flow.flow import FlowDiagram
from .base_listener import BaseListener

logger = logging.getLogger(__name__)

class DirectoryEventHandler(FileSystemEventHandler):
    """Handler per gli eventi del file system"""
    
    def __init__(self, config_file, global_context, event_config):
        self.config_file = config_file
        self.global_context = global_context
        self.event_config = event_config
        self.file_patterns = event_config.get("file_patterns", ["*"])
        self.ignore_patterns = event_config.get("ignore_patterns", [])
        
    def should_process_file(self, file_path):
        """Verifica se il file deve essere processato in base ai pattern"""
        file_name = os.path.basename(file_path)
        
        # Verifica pattern di esclusione
        for ignore_pattern in self.ignore_patterns:
            if self._match_pattern(file_name, ignore_pattern):
                return False
                
        # Verifica pattern di inclusione
        for pattern in self.file_patterns:
            if self._match_pattern(file_name, pattern):
                return True
                
        return False
    
    def _match_pattern(self, filename, pattern):
        """Semplice matching di pattern con wildcard"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def process_event(self, event_type, file_path):
        """Processa un evento del file system"""
        if not self.should_process_file(file_path):
            return
            
        logger.info(f"Evento {event_type} rilevato per: {file_path}")
        
        try:
            # Carica la configurazione del flusso
            with open(self.config_file, 'r') as file:
                config = safe_load(file)
            
            # Crea il flusso con le variabili dell'evento
            flow = FlowDiagram(config, self.global_context)
            flow.variables.update({
                'event_type': event_type,
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_dir': os.path.dirname(file_path),
                'timestamp': time.time()
            })
            
            # Esegui il flusso
            flow.run()
            
        except Exception as e:
            logger.error(f"Errore durante l'elaborazione dell'evento {event_type} per {file_path}: {e}")
    
    def on_created(self, event):
        if not event.is_directory:
            self.process_event('created', event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.process_event('modified', event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.process_event('deleted', event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            self.process_event('moved', event.dest_path)


class DirectoryListener(BaseListener):
    """
    Listener per monitorare cambiamenti in una directory.
    Utile per automazioni che devono reagire a modifiche di file.
    """
    
    def __init__(self, event_config, global_context=None):
        super().__init__(event_config, global_context)
        self.watch_path = event_config.get("watch_path", ".")
        self.recursive = event_config.get("recursive", True)
        self.poll_interval = event_config.get("poll_interval", 1.0)
        
    def listen(self, config_file):
        """
        Avvia il monitoraggio della directory specificata.
        Quando rileva cambiamenti, esegue il flusso configurato.
        """
        logger.info(f"Avvio monitoraggio directory: {self.watch_path}")
        logger.info(f"Ricorsivo: {self.recursive}")
        logger.info(f"Pattern file: {self.event_config.get('file_patterns', ['*'])}")
        logger.info(f"Pattern ignorati: {self.event_config.get('ignore_patterns', [])}")
        
        # Verifica che la directory esista
        if not os.path.exists(self.watch_path):
            logger.error(f"Directory non trovata: {self.watch_path}")
            return
            
        # Crea l'handler per gli eventi
        event_handler = DirectoryEventHandler(
            config_file, 
            self.global_context, 
            self.event_config
        )
        
        # Configura l'observer
        observer = Observer()
        observer.schedule(
            event_handler, 
            self.watch_path, 
            recursive=self.recursive
        )
        
        try:
            # Avvia il monitoraggio
            observer.start()
            logger.info("Monitoraggio directory avviato. Premi Ctrl+C per fermare.")
            
            # Mantieni il processo attivo
            while True:
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("Interruzione richiesta dall'utente")
        except Exception as e:
            logger.error(f"Errore durante il monitoraggio: {e}")
        finally:
            observer.stop()
            observer.join()
            logger.info("Monitoraggio directory terminato")


class PollingDirectoryListener(BaseListener):
    """
    Versione alternativa che usa polling invece di eventi del sistema.
    Utile quando watchdog non è disponibile o per sistemi con limitazioni.
    """
    
    def __init__(self, event_config, global_context=None):
        super().__init__(event_config, global_context)
        self.watch_path = event_config.get("watch_path", ".")
        self.poll_interval = event_config.get("poll_interval", 5.0)
        self.file_patterns = event_config.get("file_patterns", ["*"])
        self.ignore_patterns = event_config.get("ignore_patterns", [])
        self.last_scan = {}
        
    def should_process_file(self, file_path):
        """Verifica se il file deve essere processato in base ai pattern"""
        import fnmatch
        file_name = os.path.basename(file_path)
        
        # Verifica pattern di esclusione
        for ignore_pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_name, ignore_pattern):
                return False
                
        # Verifica pattern di inclusione
        for pattern in self.file_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True
                
        return False
    
    def scan_directory(self):
        """Scansiona la directory e rileva i cambiamenti"""
        current_scan = {}
        
        try:
            for root, dirs, files in os.walk(self.watch_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.should_process_file(file_path):
                        try:
                            stat = os.stat(file_path)
                            current_scan[file_path] = {
                                'mtime': stat.st_mtime,
                                'size': stat.st_size
                            }
                        except OSError:
                            # File potrebbe essere stato eliminato durante la scansione
                            continue
        except Exception as e:
            logger.error(f"Errore durante la scansione della directory: {e}")
            return
        
        # Rileva i cambiamenti
        changes = []
        
        # File nuovi o modificati
        for file_path, info in current_scan.items():
            if file_path not in self.last_scan:
                changes.append(('created', file_path))
            elif (self.last_scan[file_path]['mtime'] != info['mtime'] or 
                  self.last_scan[file_path]['size'] != info['size']):
                changes.append(('modified', file_path))
        
        # File eliminati
        for file_path in self.last_scan:
            if file_path not in current_scan:
                changes.append(('deleted', file_path))
        
        self.last_scan = current_scan
        return changes
    
    def process_change(self, event_type, file_path, config_file):
        """Processa un cambiamento rilevato"""
        logger.info(f"Evento {event_type} rilevato per: {file_path}")
        
        try:
            # Carica la configurazione del flusso
            with open(config_file, 'r') as file:
                config = safe_load(file)
            
            # Crea il flusso con le variabili dell'evento
            flow = FlowDiagram(config, self.global_context)
            flow.variables.update({
                'event_type': event_type,
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_dir': os.path.dirname(file_path),
                'timestamp': time.time()
            })
            
            # Esegui il flusso
            flow.run()
            
        except Exception as e:
            logger.error(f"Errore durante l'elaborazione dell'evento {event_type} per {file_path}: {e}")
    
    def listen(self, config_file):
        """
        Avvia il monitoraggio tramite polling della directory specificata.
        """
        logger.info(f"Avvio monitoraggio directory (polling): {self.watch_path}")
        logger.info(f"Intervallo polling: {self.poll_interval} secondi")
        logger.info(f"Pattern file: {self.file_patterns}")
        logger.info(f"Pattern ignorati: {self.ignore_patterns}")
        
        # Verifica che la directory esista
        if not os.path.exists(self.watch_path):
            logger.error(f"Directory non trovata: {self.watch_path}")
            return
        
        # Scansione iniziale
        self.scan_directory()
        logger.info("Scansione iniziale completata")
        
        try:
            while True:
                time.sleep(self.poll_interval)
                
                changes = self.scan_directory()
                if changes:
                    for event_type, file_path in changes:
                        self.process_change(event_type, file_path, config_file)
                        
        except KeyboardInterrupt:
            logger.info("Interruzione richiesta dall'utente")
        except Exception as e:
            logger.error(f"Errore durante il monitoraggio: {e}")
        finally:
            logger.info("Monitoraggio directory terminato")
