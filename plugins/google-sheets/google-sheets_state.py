"""
Google Sheets Plugin per IntellyHub
Permette di leggere, scrivere e cercare dati in Google Sheets
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Union
from flow.states.base_state import BaseState

# Import Google APIs
try:
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    # Fallback per quando le dipendenze non sono installate
    logging.warning("Google APIs non installate. Installare: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    Request = None
    service_account = None
    build = None
    HttpError = Exception

logger = logging.getLogger(__name__)

class GoogleSheetsState(BaseState):
    state_type = "google_sheets"
    
    """
    Stato per interagire con Google Sheets
    
    Configurazione YAML:
    ```yaml
    read_sheet:
      state_type: google_sheets
      action: "read"  # read, write, search, append, clear, create_sheet
      spreadsheet_id: "{SHEET_ID}"
      sheet_name: "Sheet1"  # opzionale
      range: "A1:E100"  # opzionale 
      credentials_json: "{GOOGLE_SERVICE_ACCOUNT_KEY}"  # o credentials_path
      output: "sheet_data"
      success_transition: "process_data"
      error_transition: "handle_error"
    ```
    """
    
    # Scopes necessari per Google Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, name: str, config: Dict[str, Any], global_context: Dict[str, Any]):
        super().__init__(name, config, global_context)
        
        self.action = self.state_config.get('action', 'read')
        self.spreadsheet_id = self.state_config.get('spreadsheet_id')
        self.sheet_name = self.state_config.get('sheet_name', 'Sheet1')
        self.range = self.state_config.get('range')
        self.values = self.state_config.get('values', [])
        self.search_query = self.state_config.get('search_query')
        self.search_column = self.state_config.get('search_column')
        
        # Credenziali
        self.credentials_json = self.state_config.get('credentials_json')
        self.credentials_path = self.state_config.get('credentials_path')
        
        self._service = None
        
    def _get_credentials(self, variables: Dict[str, Any]):
        """Ottiene le credenziali Google dal config o variabili ambiente"""
        try:
            # Risolvi placeholder
            creds_json = self.format_recursive(self.credentials_json, variables) if self.credentials_json else None
            creds_path = self.format_recursive(self.credentials_path, variables) if self.credentials_path else None
            
            # Prova con JSON delle credenziali
            if creds_json:
                if isinstance(creds_json, str):
                    creds_info = json.loads(creds_json)
                else:
                    creds_info = creds_json
                return service_account.Credentials.from_service_account_info(
                    creds_info, scopes=self.SCOPES)
            
            # Prova con percorso file
            if creds_path and os.path.exists(creds_path):
                return service_account.Credentials.from_service_account_file(
                    creds_path, scopes=self.SCOPES)
            
            # Prova con variabili ambiente
            if 'GOOGLE_SERVICE_ACCOUNT_KEY' in os.environ:
                creds_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_KEY'])
                return service_account.Credentials.from_service_account_info(
                    creds_info, scopes=self.SCOPES)
            
            if 'GOOGLE_CREDENTIALS_PATH' in os.environ:
                creds_path = os.environ['GOOGLE_CREDENTIALS_PATH']
                if os.path.exists(creds_path):
                    return service_account.Credentials.from_service_account_file(
                        creds_path, scopes=self.SCOPES)
            
            raise ValueError("Credenziali Google non trovate. Configurare credentials_json, credentials_path o variabili ambiente.")
            
        except Exception as e:
            logger.error(f"❌ Errore nel caricamento credenziali: {e}")
            raise
    
    def _get_service(self, variables: Dict[str, Any]):
        """Ottiene il servizio Google Sheets API"""
        if self._service is None:
            credentials = self._get_credentials(variables)
            self._service = build('sheets', 'v4', credentials=credentials)
        return self._service
    
    def _build_range(self, sheet_name: str, range_spec: Optional[str] = None) -> str:
        """Costruisce il range completo per le API"""
        if range_spec:
            return f"'{sheet_name}'!{range_spec}"
        else:
            return f"'{sheet_name}'"
    
    def _read_sheet(self, service, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Legge dati dal foglio"""
        try:
            spreadsheet_id = self.format_recursive(self.spreadsheet_id, variables)
            sheet_name = self.format_recursive(self.sheet_name, variables)
            range_spec = self.format_recursive(self.range, variables) if self.range else None
            
            range_name = self._build_range(sheet_name, range_spec)
            
            logger.info(f"📖 Lettura Google Sheets: {spreadsheet_id} - {range_name}")
            
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            return {
                'success': True,
                'data': values,
                'range': range_name,
                'rows_count': len(values),
                'columns_count': len(values[0]) if values else 0
            }
            
        except HttpError as e:
            error_msg = f"Errore Google Sheets API: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Errore nella lettura: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _write_sheet(self, service, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Scrive dati nel foglio"""
        try:
            spreadsheet_id = self.format_recursive(self.spreadsheet_id, variables)
            sheet_name = self.format_recursive(self.sheet_name, variables)
            range_spec = self.format_recursive(self.range, variables) if self.range else None
            values = self.format_recursive(self.values, variables)
            
            if not values:
                return {'success': False, 'error': 'Nessun valore da scrivere specificato'}
            
            range_name = self._build_range(sheet_name, range_spec) if range_spec else f"'{sheet_name}'"
            
            logger.info(f"✍️ Scrittura Google Sheets: {spreadsheet_id} - {range_name}")
            
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            
            return {
                'success': True,
                'updated_cells': updated_cells,
                'updated_range': result.get('updatedRange'),
                'updated_rows': result.get('updatedRows', 0),
                'updated_columns': result.get('updatedColumns', 0)
            }
            
        except HttpError as e:
            error_msg = f"Errore Google Sheets API: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Errore nella scrittura: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _append_sheet(self, service, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Aggiunge dati alla fine del foglio"""
        try:
            spreadsheet_id = self.format_recursive(self.spreadsheet_id, variables)
            sheet_name = self.format_recursive(self.sheet_name, variables)
            values = self.format_recursive(self.values, variables)
            
            if not values:
                return {'success': False, 'error': 'Nessun valore da aggiungere specificato'}
            
            range_name = f"'{sheet_name}'"
            
            logger.info(f"➕ Append Google Sheets: {spreadsheet_id} - {range_name}")
            
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return {
                'success': True,
                'updated_cells': result.get('updates', {}).get('updatedCells', 0),
                'updated_range': result.get('updates', {}).get('updatedRange'),
                'appended_rows': len(values)
            }
            
        except HttpError as e:
            error_msg = f"Errore Google Sheets API: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Errore nell'append: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _clear_sheet(self, service, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Pulisce i dati dal foglio"""
        try:
            spreadsheet_id = self.format_recursive(self.spreadsheet_id, variables)
            sheet_name = self.format_recursive(self.sheet_name, variables)
            range_spec = self.format_recursive(self.range, variables) if self.range else None
            
            range_name = self._build_range(sheet_name, range_spec) if range_spec else f"'{sheet_name}'"
            
            logger.info(f"🗑️ Pulizia Google Sheets: {spreadsheet_id} - {range_name}")
            
            result = service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                body={}
            ).execute()
            
            return {
                'success': True,
                'cleared_range': result.get('clearedRange')
            }
            
        except HttpError as e:
            error_msg = f"Errore Google Sheets API: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Errore nella pulizia: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _search_sheet(self, service, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Cerca dati nel foglio"""
        try:
            # Prima leggi i dati
            read_result = self._read_sheet(service, variables)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            search_query = self.format_recursive(self.search_query, variables)
            search_column = self.format_recursive(self.search_column, variables) if self.search_column else None
            
            if not search_query:
                return {'success': False, 'error': 'Query di ricerca non specificata'}
            
            logger.info(f"🔍 Ricerca in Google Sheets: '{search_query}' in colonna {search_column or 'tutte'}")
            
            matches = []
            
            for row_idx, row in enumerate(data):
                if search_column:
                    # Ricerca in colonna specifica
                    col_idx = self._column_to_index(search_column) if search_column.isalpha() else None
                    if col_idx is not None and col_idx < len(row):
                        if search_query.lower() in str(row[col_idx]).lower():
                            matches.append({
                                'row': row_idx + 1,
                                'column': search_column,
                                'value': row[col_idx],
                                'full_row': row
                            })
                    elif search_column in row:  # Cerca per nome header
                        if search_query.lower() in str(row[search_column]).lower():
                            matches.append({
                                'row': row_idx + 1,
                                'column': search_column,
                                'value': row[search_column],
                                'full_row': row
                            })
                else:
                    # Ricerca in tutte le colonne
                    for col_idx, cell in enumerate(row):
                        if search_query.lower() in str(cell).lower():
                            matches.append({
                                'row': row_idx + 1,
                                'column': self._index_to_column(col_idx),
                                'value': cell,
                                'full_row': row
                            })
                            break  # Una match per riga
            
            return {
                'success': True,
                'matches': matches,
                'matches_count': len(matches),
                'search_query': search_query,
                'search_column': search_column
            }
            
        except Exception as e:
            error_msg = f"Errore nella ricerca: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _create_sheet(self, service, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuovo foglio nel documento"""
        try:
            spreadsheet_id = self.format_recursive(self.spreadsheet_id, variables)
            sheet_name = self.format_recursive(self.sheet_name, variables)
            
            logger.info(f"📄 Creazione nuovo foglio: {sheet_name}")
            
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            sheet_id = result.get('replies', [{}])[0].get('addSheet', {}).get('properties', {}).get('sheetId')
            
            return {
                'success': True,
                'sheet_name': sheet_name,
                'sheet_id': sheet_id
            }
            
        except HttpError as e:
            error_msg = f"Errore Google Sheets API: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Errore nella creazione foglio: {e}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _column_to_index(self, column: str) -> int:
        """Converte lettera colonna (A, B, AA) in indice numerico (0, 1, 26)"""
        result = 0
        for char in column.upper():
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1
    
    def _index_to_column(self, index: int) -> str:
        """Converte indice numerico (0, 1, 26) in lettera colonna (A, B, AA)"""
        result = ""
        index += 1
        while index > 0:
            index -= 1
            result = chr(ord('A') + index % 26) + result
            index //= 26
        return result
    
    def execute(self, variables: Dict[str, Any]) -> str:
        """
        Esegue l'operazione Google Sheets
        
        Args:
            variables: Variabili del contesto
            
        Returns:
            Nome dello stato successivo
        """
        
        # Esegui logging se configurato
        self.log_if_configured(variables)
        
        try:
            if not build:
                return self.state_config.get('error_transition', 'error')
            
            service = self._get_service(variables)
            action = self.format_recursive(self.action, variables)
            
            # Esegui l'azione specifica
            result = None
            if action == 'read':
                result = self._read_sheet(service, variables)
            elif action == 'write':
                result = self._write_sheet(service, variables)
            elif action == 'append':
                result = self._append_sheet(service, variables)
            elif action == 'clear':
                result = self._clear_sheet(service, variables)
            elif action == 'search':
                result = self._search_sheet(service, variables)
            elif action == 'create_sheet':
                result = self._create_sheet(service, variables)
            else:
                result = {'success': False, 'error': f"Azione non supportata: {action}"}
            
            # Salva il risultato nella variabile di output
            if self.state_config.get('output'):
                variables[self.state_config['output']] = result
            
            # Determina la transizione
            if result.get('success', False):
                logger.info(f"✅ Operazione Google Sheets '{action}' completata con successo")
                return self.state_config.get('success_transition', self.state_config.get('transition'))
            else:
                logger.error(f"❌ Operazione Google Sheets '{action}' fallita: {result.get('error', 'Errore sconosciuto')}")
                return self.state_config.get('error_transition', 'error')
                
        except Exception as e:
            error_msg = f"Errore inaspettato in Google Sheets: {e}"
            logger.error(f"❌ {error_msg}")
            
            if self.state_config.get('output'):
                variables[self.state_config['output']] = {
                    'success': False,
                    'error': error_msg
                }
            
            return self.state_config.get('error_transition', 'error')
    
    def validate_config(self) -> bool:
        """Valida la configurazione dello stato"""
        required_fields = ['action', 'spreadsheet_id']
        missing_fields = [field for field in required_fields if not self.state_config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campi mancanti in google_sheets state: {', '.join(missing_fields)}")
        
        # Validazione azione
        valid_actions = ['read', 'write', 'search', 'append', 'clear', 'create_sheet']
        if self.action not in valid_actions:
            raise ValueError(f"Azione non valida '{self.action}'. Azioni supportate: {', '.join(valid_actions)}")
        
        # Validazioni specifiche per azione
        if self.action in ['write', 'append'] and not self.values:
            raise ValueError(f"L'azione '{self.action}' richiede il parametro 'values'")
        
        if self.action == 'search' and not self.search_query:
            raise ValueError("L'azione 'search' richiede il parametro 'search_query'")
        
        return True