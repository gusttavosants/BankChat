from langchain.tools import tool
from agents.cambio.service import CambioService
from exceptions.cambio_exceptions import APIIndisponivelError, MoedaNaoSuportadaError

cambio_service = CambioService()

@tool
def consultar_cotacao(moeda: str) -> dict:
    """Consulta a cotação atual de uma moeda (USD, EUR, GBP, BTC) em relação ao Real (BRL)."""
    try:
        resultado = cambio_service.consultar_cotacao(moeda)
        return {
            "status_code": 200,
            "message": "Cotação obtida com sucesso.",
            "data": resultado
        }
    except MoedaNaoSuportadaError as e:
        return {
            "status_code": 400,
            "message": str(e),
            "data": None
        }
    except APIIndisponivelError as e:
        return {
            "status_code": 503,
            "message": str(e),
            "data": None
        }
    except Exception as e:
        from utils.logger import log_erro
        log_erro("tools.consultar_cotacao", e)
        return {
            "status_code": 500,
            "message": "Erro interno ao consultar cotação. Tente novamente mais tarde.",
            "data": None
        }
