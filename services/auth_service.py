from utils.validators import validar_cpf, validar_data_nascimento
from utils.formatters import formatar_cpf
from repositories.clientes_repository import ClientesRepository
from exceptions.auth_exceptions import ClienteNaoEncontradoError, CredenciaisInvalidasError

class AuthService:
    def __init__(self, clientes_repo: ClientesRepository = None):
        self.clientes_repo = clientes_repo or ClientesRepository()

    def autenticar(self, cpf: str, data_nascimento: str) -> dict:
        if not validar_cpf(cpf):
            raise CredenciaisInvalidasError("CPF inválido.")
        if not validar_data_nascimento(data_nascimento):
            raise CredenciaisInvalidasError("Data de nascimento inválida.")

        cpf_formatado = formatar_cpf(cpf)
        cliente = self.clientes_repo.get_by_cpf(cpf_formatado)
        
        if not cliente:
            raise ClienteNaoEncontradoError("Cliente não encontrado.")
            
        if cliente['data_nascimento'] != data_nascimento:
            raise CredenciaisInvalidasError("Credenciais inválidas.")
            
        return cliente
