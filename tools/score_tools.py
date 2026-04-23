from langchain.tools import tool
from services.score_service import ScoreService
from exceptions.auth_exceptions import ClienteNaoEncontradoError

score_service = ScoreService()

@tool
def calcular_score(renda: float, tipo_emprego: str, despesas: float, dependentes: str, tem_dividas: str) -> dict:
    """Calcula um novo score financeiro baseado na renda, tipo de emprego (formal/autônomo/desempregado), despesas fixas, número de dependentes (0,1,2,3+) e se tem dívidas (sim/não)."""
    try:
        resultado = score_service.calcular_score(float(renda), tipo_emprego, float(despesas), str(dependentes), str(tem_dividas))
        return {
            "status_code": 200,
            "message": "Score calculado com sucesso.",
            "data": resultado
        }
    except ValueError as e:
        return {
            "status_code": 400,
            "message": str(e),
            "data": None
        }
    except Exception as e:
        from utils.logger import log_erro
        log_erro("tools.calcular_score", e)
        return {
            "status_code": 500,
            "message": "Erro interno ao calcular score.",
            "data": None
        }

@tool
def atualizar_score(cpf: str, novo_score: int) -> dict:
    """Atualiza o score de crédito do cliente no banco de dados."""
    try:
        resultado = score_service.atualizar_score(cpf, int(novo_score))
        return {
            "status_code": 200,
            "message": "Score atualizado com sucesso.",
            "data": resultado
        }
    except ClienteNaoEncontradoError:
        return {
            "status_code": 404,
            "message": "Cliente não encontrado. Score não atualizado.",
            "data": None
        }
    except Exception as e:
        from utils.logger import log_erro
        log_erro("tools.atualizar_score", e)
        return {
            "status_code": 500,
            "message": "Erro técnico ao persistir dados. Contate o suporte.",
            "data": None
        }
