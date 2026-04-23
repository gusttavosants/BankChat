import json
from langchain.tools import tool
from services.auth_service import AuthService
from exceptions.auth_exceptions import ClienteNaoEncontradoError, CredenciaisInvalidasError
from utils.logger import log_erro

auth_service = AuthService()

@tool
def verificar_cpf(cpf: str) -> str:
    """Valida se o CPF existe na base cadastral."""
    try:
        if auth_service.verificar_cpf(cpf):
            return json.dumps({"status_code": 200, "message": "OK"})
        return json.dumps({"status_code": 404, "message": "Inexistente"})
    except Exception as e:
        log_erro("tools.verificar_cpf", e)
        return json.dumps({"status_code": 500})

@tool
def autenticar_cliente(cpf: str, data_nascimento: str) -> str:
    """Realiza a autenticação completa do cliente."""
    try:
        cliente = auth_service.autenticar(cpf, data_nascimento)
        return json.dumps({"status_code": 200, "data": cliente})
    except (CredenciaisInvalidasError, ClienteNaoEncontradoError) as e:
        return json.dumps({"status_code": 401, "message": str(e)})
    except Exception as e:
        log_erro("tools.autenticar_cliente", e)
        return json.dumps({"status_code": 500})
