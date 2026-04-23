import pytest
from unittest.mock import patch
from services.cambio_service import CambioService
from exceptions.cambio_exceptions import MoedaNaoSuportadaError, APIIndisponivelError

def test_moeda_nao_suportada():
    service = CambioService()
    with pytest.raises(MoedaNaoSuportadaError):
        service.consultar_cotacao("ARS")

@patch("requests.get")
def test_consultar_cotacao_sucesso(mock_get):
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {
                "USDBRL": {
                    "bid": "5.00",
                    "ask": "5.05",
                    "create_date": "2026-04-22T00:00:00"
                }
            }
            
    mock_get.return_value = MockResponse()
    service = CambioService()
    res = service.consultar_cotacao("USD")
    assert res["valor_compra"] == 5.00
