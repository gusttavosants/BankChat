from langchain.tools import tool
from services.credito_service import CreditoService
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from exceptions.credito_exceptions import ScoreInsuficienteError, ErroAoGravarSolicitacaoError

credito_service = CreditoService()

@tool
def consultar_limite(cpf: str) -> dict:
    """Consulta o limite atual de crédito de um cliente usando seu CPF."""
    try:
        cliente = credito_service.consultar_limite(cpf)
        return {
            "status_code": 200,
            "message": "Limite consultado com sucesso.",
            "data": {
                "cpf": cliente['cpf'],
                "limite_atual": float(cliente['limite_credito']),
                "score_credito": int(cliente['score_credito'])
            }
        }
    except ClienteNaoEncontradoError:
        return {
            "status_code": 404,
            "message": "Cliente não encontrado na base de dados.",
            "data": None
        }

@tool
def solicitar_aumento(cpf: str, novo_limite: float) -> dict:
    """Grava uma solicitação de aumento de limite para o cliente especificado."""
    try:
        solicitacao = credito_service.solicitar_aumento(cpf, float(novo_limite))
        return {
            "status_code": 201,
            "message": "Solicitação de aumento registrada com sucesso.",
            "data": solicitacao
        }
    except ClienteNaoEncontradoError:
        return {
            "status_code": 404,
            "message": "Cliente não encontrado na base de dados.",
            "data": None
        }
    except ErroAoGravarSolicitacaoError:
        return {
            "status_code": 500,
            "message": "Erro interno ao registrar solicitação.",
            "data": None
        }

@tool
def verificar_score_limite(score: int, limite_solicitado: float) -> dict:
    """Verifica se o score atual do cliente permite o novo limite solicitado."""
    try:
        resultado = credito_service.verificar_score(int(score), float(limite_solicitado))
        return {
            "status_code": 200,
            "message": "Score suficiente. Solicitação aprovada.",
            "data": resultado
        }
    except ScoreInsuficienteError:
        return {
            "status_code": 422,
            "message": "Score insuficiente para o limite solicitado.",
            "data": {
                "status_pedido": "rejeitado",
                "score_atual": score,
                "novo_limite_solicitado": limite_solicitado
            }
        }
