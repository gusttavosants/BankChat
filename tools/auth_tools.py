from langchain.tools import tool
from services.auth_service import AuthService
from exceptions.auth_exceptions import ClienteNaoEncontradoError, CredenciaisInvalidasError

auth_service = AuthService()

@tool
def verificar_cpf(cpf: str) -> dict:
    """Verifica se um CPF está cadastrado na base de dados do Banco Ágil."""
    try:
        if auth_service.verificar_cpf(cpf):
            return {
                "status_code": 200,
                "message": "CPF localizado com sucesso.",
                "data": {"cpf_valido": True}
            }
        else:
            return {
                "status_code": 404,
                "message": "CPF não encontrado ou inválido.",
                "data": {"cpf_valido": False}
            }
    except Exception as e:
        from utils.logger import log_erro
        log_erro("tools.verificar_cpf", e)
        return {
            "status_code": 500,
            "message": "Erro técnico ao verificar CPF.",
            "data": None
        }

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
        from utils.logger import log_erro
        log_erro("tools.autenticar_cliente", e)
        return {
            "status_code": 500,
            "message": "Erro interno ao autenticar.",
            "data": None
        }
