import logging
import os
from datetime import datetime

# Configuração básica de logs
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'errors.log')

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('BancoAgil')

def log_erro(contexto: str, erro: Exception):
    """Registra um erro no arquivo de log com o contexto fornecido."""
    msg = f"[{contexto}] {type(erro).__name__}: {str(erro)}"
    logger.error(msg)
    print(f"DEBUG LOG: {msg}") # Para visualização no terminal do VS Code
