import pytest
from services.score_service import ScoreService

class DummyClientesRepo:
    def get_by_cpf(self, cpf):
        if cpf == "123.456.789-00":
            return {"score_credito": 500, "limite_credito": 3000.0}
        return None
    def update_score_e_limite(self, cpf, score, limite):
        pass

def test_calcular_score_logica():
    service = ScoreService(DummyClientesRepo())
    res = service.calcular_score(3000.0, "formal", 1000.0, "1", "não")
    assert "score_calculado" in res
    assert res["score_calculado"] > 0

def test_atualizar_score():
    service = ScoreService(DummyClientesRepo())
    res = service.atualizar_score("123.456.789-00", 600)
    assert res["score_novo"] == 600
    assert res["score_anterior"] == 500
