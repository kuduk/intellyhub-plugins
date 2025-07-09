import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseState:
    """Classe base per tutti gli stati del sistema FSM."""
    
    def __init__(self, name: str, state_config: Dict[str, Any], global_context: Dict[str, Any]):
        self.name = name
        self.state_config = state_config
        self.global_context = global_context
        
    def format_recursive(self, value, variables):
        """Formatta ricorsivamente le stringhe con le variabili."""
        if isinstance(value, str):
            # Sostituisce le variabili nel formato {variable_name}
            def replace_var(match):
                var_name = match.group(1)
                if var_name in variables:
                    return str(variables[var_name])
                return match.group(0)  # Restituisce il placeholder originale se la variabile non esiste
            
            return re.sub(r'\{([^}]+)\}', replace_var, value)
        elif isinstance(value, dict):
            return {k: self.format_recursive(v, variables) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.format_recursive(item, variables) for item in value]
        else:
            return value
    
    def execute(self, variables: Dict[str, Any]) -> str:
        """Esegue lo stato. Deve essere implementato dalle sottoclassi."""
        raise NotImplementedError("Le sottoclassi devono implementare il metodo execute")
