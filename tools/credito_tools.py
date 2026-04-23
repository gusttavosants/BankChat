import json
from langchain.tools import tool
from services.credito_service import CreditoService
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from exceptions.credito_exceptions import ScoreInsuficienteError
from utils.logger import log_erro

service = CreditoService()

@tool
def consultar_limite(cpf: str) -> str:
    """Retorna os dados de limite e score do cliente."""
    try:
        cli = service.consultar_limite(cpf)
        return json.dumps({
            "status_code": 200, 
            "data": {
                "cpf": cli['cpf'], 
                "limite": cli['limite_credito'], 
                "score": cli['score_credito']
            }
        })
    except Exception as e:
        log_erro("tools.consultar_limite", e)
        return json.dumps({"status_code": 404})

@tool
def solicitar_aumento(cpf: str, novo_limite: float) -> str:
    """Registra um pedido de aumento de limite."""
    try:
        solicitacao = service.solicitar_aumento(cpf, float(novo_limite))
        return json.dumps({"status_code": 201, "data": solicitacao})
    except Exception as e:
        log_erro("tools.solicitar_aumento", e)
        return json.dumps({"status_code": 500})

@tool
def verificar_score_limite(score: int, limite_solicitado: float = None) -> str:
    """Valida se o score comporta o limite solicitado."""
    try:
        valor = float(limite_solicitado) if limite_solicitado else 0.0
        res = service.verificar_score(int(score), valor)
        return json.dumps({"status_code": 200, "data": res})
    except ScoreInsuficienteError as e:
        limite_max = service.score_repo.get_limite_maximo(int(score))
        return json.dumps({
            "status_code": 422, 
            "data": {"limite_maximo": limite_max}
        })
    except Exception as e:
        log_erro("tools.verificar_score_limite", e)
        return json.dumps({"status_code": 500})
