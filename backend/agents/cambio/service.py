import requests
import time
from datetime import datetime, timedelta
from exceptions.cambio_exceptions import APIIndisponivelError, MoedaNaoSuportadaError
from utils.logger import log_erro

class CambioService:
    _cache = {}
    CACHE_TTL = 300 # 5 minutos

    def consultar_cotacao(self, moeda: str) -> dict:
        moeda = moeda.upper()
        moedas_suportadas = ["USD", "EUR", "GBP", "BTC"]
        
        if moeda not in moedas_suportadas:
            raise MoedaNaoSuportadaError("Moeda não suportada. Disponíveis: USD, EUR, GBP, BTC.")
            
        # 1. Verifica Cache
        agora = datetime.now()
        if moeda in self._cache:
            dados, expira = self._cache[moeda]
            if agora < expira:
                return dados

        url = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        tentativas = 3
        for i in range(tentativas):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                key = f"{moeda}BRL"
                
                if key not in data:
                    raise APIIndisponivelError("Formato de resposta inesperado da API.")
                    
                info = data[key]
                resultado = {
                    "moeda": moeda,
                    "moeda_destino": "BRL",
                    "valor_compra": float(info.get("bid", 0)),
                    "valor_venda": float(info.get("ask", 0)),
                    "timestamp": info.get("create_date", agora.isoformat())
                }
                
                # 2. Salva no Cache
                self._cache[moeda] = (resultado, agora + timedelta(seconds=self.CACHE_TTL))
                
                return resultado

            except requests.RequestException as e:
                log_erro(f"CambioService.consultar_cotacao ({moeda} - tentativa {i+1})", e)
                
                # Se for erro 429 (Rate Limit), espera mais tempo
                wait_time = (i + 1) * 2 
                if i < tentativas - 1:
                    time.sleep(wait_time)
                    continue
                
                raise APIIndisponivelError("O serviço de câmbio está com alta demanda. Por favor, tente novamente em alguns minutos.")
