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
    """Grava uma solicitação de aumento de limite e verifica automaticamente a compatibilidade do score."""
    try:
        # Primeiro verificamos se o score permite (para dar feedback imediato)
        cliente = credito_service.consultar_limite(cpf)
        score_atual = int(cliente['score_credito'])
        
        try:
            credito_service.verificar_score(score_atual, float(novo_limite))
            score_status = "compatível"
        except ScoreInsuficienteError:
            score_status = "insuficiente"

        solicitacao = credito_service.solicitar_aumento(cpf, float(novo_limite))
        
        return {
            "status_code": 201,
            "message": "Solicitação de aumento registrada com sucesso.",
            "data": {
                **solicitacao,
                "score_status": score_status,
                "sugestao": "Oferecer entrevista de crédito" if score_status == "insuficiente" else None
            }
        }
    except ClienteNaoEncontradoError:
        return {
            "status_code": 404,
            "message": "Cliente não encontrado na base de dados.",
            "data": None
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Erro ao processar solicitação: {str(e)}",
            "data": None
        }

@tool
def verificar_score_limite(score: int, limite_solicitado: float = None) -> dict:
    """Verifica se o score atual do cliente permite o novo limite solicitado. Se limite_solicitado for None, retorna apenas o limite máximo permitido para o score."""
    try:
        # Se não informou limite, usamos um valor simbólico para pegar apenas o limite_maximo
        valor_teste = float(limite_solicitado) if limite_solicitado is not None else 0.0
        resultado = credito_service.verificar_score(int(score), valor_teste)
        
        return {
            "status_code": 200,
            "message": "Limite máximo consultado com sucesso." if limite_solicitado is None else "Score suficiente. Solicitação aprovada.",
            "data": resultado
        }
    except ScoreInsuficienteError as e:
        # Pega o limite máximo mesmo em caso de erro para informar ao usuário
        import re
        msg = str(e)
        # Se o service lançou erro, o score_repo ainda tem o dado. 
        # Vamos tentar pegar o limite máximo do erro ou do service
        limite_max = credito_service.score_repo.get_limite_maximo(int(score))
        return {
            "status_code": 422,
            "message": "Score insuficiente para o limite solicitado.",
            "data": {
                "status_pedido": "rejeitado",
                "score_atual": score,
                "limite_maximo_permitido": limite_max,
                "novo_limite_solicitado": limite_solicitado
            }
        }
