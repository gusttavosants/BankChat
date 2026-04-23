import requests
from datetime import datetime
from exceptions.cambio_exceptions import APIIndisponivelError, MoedaNaoSuportadaError

class CambioService:
    def consultar_cotacao(self, moeda: str) -> dict:
        moeda = moeda.upper()
        moedas_suportadas = ["USD", "EUR", "GBP", "BTC"]
        
        if moeda not in moedas_suportadas:
            raise MoedaNaoSuportadaError("Moeda não suportada. Disponíveis: USD, EUR, GBP, BTC.")
            
        url = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            key = f"{moeda}BRL"
            
            if key not in data:
                raise APIIndisponivelError("Formato de resposta inesperado da API.")
                
            info = data[key]
            return {
                "moeda": moeda,
                "moeda_destino": "BRL",
                "valor_compra": float(info.get("bid", 0)),
                "valor_venda": float(info.get("ask", 0)),
                "timestamp": info.get("create_date", datetime.now().isoformat())
            }
        except requests.RequestException:
            raise APIIndisponivelError("Serviço de câmbio temporariamente indisponível.")
