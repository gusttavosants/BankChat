import logging
import os

# Garante que a pasta de logs exista
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('BancoAgil')

def log_erro(ctx: str, err: Exception):
    msg = f"[{ctx}] {type(err).__name__}: {str(err)}"
    logger.error(msg)
