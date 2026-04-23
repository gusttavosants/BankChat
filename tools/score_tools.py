import json
from langchain.tools import tool
from services.score_service import ScoreService
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from utils.logger import log_erro

score_service = ScoreService()

@tool
def calcular_score(renda: float, tipo_emprego: str, despesas: float, dependentes: str, tem_dividas: str) -> str:
    """Calcula o score financeiro baseado nos dados fornecidos."""
    try:
        res = score_service.calcular_score(float(renda), tipo_emprego, float(despesas), str(dependentes), str(tem_dividas))
        return json.dumps({"status_code": 200, "data": res})
    except Exception as e:
        log_erro("tools.calcular_score", e)
        return json.dumps({"status_code": 500, "message": "Erro ao calcular score."})

@tool
def atualizar_score(cpf: str, novo_score: int) -> str:
    """Persiste o novo score no banco de dados."""
    try:
        res = score_service.atualizar_score(cpf, int(novo_score))
        return json.dumps({"status_code": 200, "data": res})
    except ClienteNaoEncontradoError:
        return json.dumps({"status_code": 404, "message": "Cliente não localizado."})
    except Exception as e:
        log_erro("tools.atualizar_score", e)
        return json.dumps({"status_code": 500, "message": "Erro na persistência."})
