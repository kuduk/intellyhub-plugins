import logging
import imaplib
import email
from email.header import decode_header
import time
from yaml import safe_load

# Importazioni dal nostro framework
from flow.flow import FlowDiagram
from .base_listener import BaseListener # Eredita dalla classe base che abbiamo definito
from flow.utils import SafeLogger

logger = SafeLogger(__name__)

class EmailListener(BaseListener):
    """
    Questo listener si connette a una casella di posta elettronica tramite IMAP,
    controlla periodicamente la presenza di nuove email non lette e,
    quando ne trova una, avvia un diagramma di flusso passando i dettagli
    dell'email come variabili.
    """
    def __init__(self, event_config, global_context=None):
        # Chiama il costruttore della classe base per primo
        super().__init__(event_config, global_context)

        # La funzione 'self.format_recursive' è ereditata da BaseListener
        self.server = self.format_recursive(self.event_config.get("server"), self.global_context)
        self.username = self.format_recursive(self.event_config.get("username"), self.global_context)
        self.password = self.format_recursive(self.event_config.get("password"), self.global_context)
        self.folder = self.format_recursive(self.event_config.get("folder", "inbox"), self.global_context)
        self.poll_interval = int(self.event_config.get("poll_interval", 60))  # in secondi
        # Aggiungo un controllo per verificare che la configurazione essenziale sia presente
        if not all([self.server, self.username, self.password]):
            raise ValueError("Configurazione per EmailListener incompleta. 'server', 'username', e 'password' sono richiesti.")

    def check_email(self):
        """
        Si connette al server IMAP e controlla l'ultima email non letta.
        Restituisce un dizionario con i dettagli dell'email o None.
        """
        mail = imaplib.IMAP4_SSL(self.server)
        mail.login(self.username, self.password)
        mail.select(self.folder)

        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK" or not messages[0]:
            mail.logout()
            return None

        latest_email_id = messages[0].split()[-1]
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        if status != "OK":
            mail.logout()
            return None
            
        mail.logout() # Chiudi la connessione il prima possibile

        msg = email.message_from_bytes(msg_data[0][1])
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        email_from = msg.get("From")
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdisp = str(part.get("Content-Disposition"))
                if ctype == "text/plain" and "attachment" not in cdisp:
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        
        # Restituisci un dizionario strutturato, è più pulito
        return {
            "email_from": email_from,
            "email_subject": subject,
            "email_body": body
        }

    def listen(self, config_file):
        """
        Metodo principale che esegue il polling della casella di posta
        in un ciclo infinito, rispettando il tuo design originale.
        """
        logger.info(f"▶️  Avvio EmailListener per l'utente '{self.username}'...")
        while True:
            try:
                email_data = self.check_email()
                if email_data:
                    logger.info(f"📨 Nuova email ricevuta da {email_data['email_from']}: {email_data['email_subject']}")

                    # Ricarica la configurazione ad ogni esecuzione, come nel tuo design
                    with open(config_file, 'r') as f:
                        config = safe_load(f)

                    # Esegui il flow
                    flow = FlowDiagram(config, self.global_context)
                    
                    # Inietta i dati dell'email nel contesto del flusso
                    flow.variables.update(email_data)
                    
                    flow.run()

            except Exception as e:
                logger.error(f"❌ Errore nel ciclo del listener email: {e}")
                # In caso di errore (es. rete), aspetta un po' di più prima di riprovare
                time.sleep(300) 
                continue

            # Aspetta 60 secondi prima del prossimo controllo
            time.sleep(self.poll_interval)
