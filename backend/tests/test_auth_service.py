import pytest
from agents.triagem.service import AuthService
from exceptions.auth_exceptions import CredenciaisInvalidasError, ClienteNaoEncontradoError

class DummyClientesRepo:
    def get_by_cpf(self, cpf: str):
        if cpf == "123.456.789-00":
            return {"cpf": cpf, "nome": "João", "data_nascimento": "15/03/1990"}
        return None

def test_autenticar_sucesso():
    service = AuthService(clientes_repo=DummyClientesRepo())
    cliente = service.autenticar("123.456.789-00", "15/03/1990")
    assert cliente["nome"] == "João"

def test_autenticar_cpf_invalido():
    service = AuthService(clientes_repo=DummyClientesRepo())
    with pytest.raises(CredenciaisInvalidasError):
        service.autenticar("123", "15/03/1990")

def test_autenticar_cliente_nao_encontrado():
    service = AuthService(clientes_repo=DummyClientesRepo())
    with pytest.raises(ClienteNaoEncontradoError):
        service.autenticar("000.000.000-00", "15/03/1990")
