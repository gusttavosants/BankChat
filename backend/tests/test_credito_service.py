import pytest
from agents.credito.service import CreditoService
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from exceptions.credito_exceptions import ScoreInsuficienteError

class DummyClientesRepo:
    def get_by_cpf(self, cpf: str):
        if cpf == "123.456.789-00":
            return {"cpf": cpf, "limite_credito": 3000.0, "score_credito": 650}
        return None

class DummyScoreRepo:
    def get_limite_maximo(self, score: int):
        if score >= 600:
            return 5000.0
        return 0.0

class DummySolicitacoesRepo:
    def save(self, solicitacao):
        return True

def test_consultar_limite_sucesso():
    service = CreditoService(DummyClientesRepo(), DummyScoreRepo(), DummySolicitacoesRepo())
    res = service.consultar_limite("123.456.789-00")
    assert res["limite_credito"] == 3000.0

def test_solicitar_aumento_sucesso():
    service = CreditoService(DummyClientesRepo(), DummyScoreRepo(), DummySolicitacoesRepo())
    res = service.solicitar_aumento("123.456.789-00", 4000.0)
    assert res["status_pedido"] == "aprovado"

def test_verificar_score_aprovado():
    service = CreditoService(DummyClientesRepo(), DummyScoreRepo(), DummySolicitacoesRepo())
    res = service.verificar_score(650, 4000.0)
    assert res["status_pedido"] == "aprovado"

def test_verificar_score_rejeitado():
    service = CreditoService(DummyClientesRepo(), DummyScoreRepo(), DummySolicitacoesRepo())
    with pytest.raises(ScoreInsuficienteError):
        service.verificar_score(650, 6000.0)
