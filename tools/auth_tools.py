from langchain.tools import tool
from services.auth_service import AuthService
from exceptions.auth_exceptions import ClienteNaoEncontradoError, CredenciaisInvalidasError

auth_service = AuthService()

@tool
def autenticar_cliente(cpf: str, data_nascimento: str) -> dict:
    """Autentica o cliente usando CPF e data de nascimento no formato DD/MM/YYYY. Retorna dados do cliente se sucesso."""
    try:
        cliente = auth_service.autenticar(cpf, data_nascimento)
        return {
            "status_code": 200,
            "message": "Cliente autenticado com sucesso.",
            "data": cliente
        }
    except CredenciaisInvalidasError as e:
        return {
            "status_code": 401,
            "message": f"Erro de autenticação: {str(e)}",
            "data": None
        }
    except ClienteNaoEncontradoError as e:
        return {
            "status_code": 404,
            "message": "Nenhum cliente encontrado com o CPF informado.",
            "data": None
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": "Erro interno ao autenticar.",
            "data": None
        }
