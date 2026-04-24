import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, 'errors.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('BancoAgil')

def log_erro(ctx: str, err: Exception):
    msg = f"[{ctx}] {type(err).__name__}: {str(err)}"
    logger.error(msg)
