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

        # 2. Tenta AwesomeAPI (Primária)
        try:
            resultado = self._consultar_awesome_api(moeda)
            self._cache[moeda] = (resultado, agora + timedelta(seconds=self.CACHE_TTL))
            return resultado
        except Exception as e:
            log_erro(f"AwesomeAPI falhou para {moeda}, tentando fallback...", e)
            
        # 3. Fallback (Secundária)
        try:
            if moeda == "BTC":
                resultado = self._consultar_coingecko(moeda)
            else:
                resultado = self._consultar_frankfurter(moeda)
            
            self._cache[moeda] = (resultado, agora + timedelta(seconds=self.CACHE_TTL))
            return resultado
        except Exception as e:
            log_erro(f"Fallback também falhou para {moeda}", e)
            raise APIIndisponivelError("O serviço de câmbio está temporariamente indisponível em todos os nossos provedores. Por favor, tente novamente mais tarde.")

    def _consultar_awesome_api(self, moeda: str) -> dict:
        url = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        data = response.json()
        info = data[f"{moeda}BRL"]
        return {
            "moeda": moeda,
            "moeda_destino": "BRL",
            "valor_compra": float(info.get("bid", 0)),
            "valor_venda": float(info.get("ask", 0)),
            "timestamp": info.get("create_date", datetime.now().isoformat())
        }

    def _consultar_frankfurter(self, moeda: str) -> dict:
        # Frankfurter usa BRL como destino, suporta USD, EUR, GBP
        url = f"https://api.frankfurter.app/latest?from={moeda}&to=BRL"
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()
        valor = data["rates"]["BRL"]
        return {
            "moeda": moeda,
            "moeda_destino": "BRL",
            "valor_compra": float(valor),
            "valor_venda": float(valor),
            "timestamp": f"{data['date']} (via Frankfurter)"
        }

    def _consultar_coingecko(self, moeda: str) -> dict:
        # Moeda deve ser 'bitcoin' para o coingecko
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()
        valor = data["bitcoin"]["brl"]
        return {
            "moeda": "BTC",
            "moeda_destino": "BRL",
            "valor_compra": float(valor),
            "valor_venda": float(valor),
            "timestamp": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (via CoinGecko)"
        }
