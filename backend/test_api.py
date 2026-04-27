import requests

def test_api():
    moedas = ["USD", "EUR", "GBP", "BTC"]
    for moeda in moedas:
        url = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
        try:
            response = requests.get(url, timeout=5)
            print(f"{moeda}: {response.status_code}")
            if response.status_code == 200:
                print(f"Data: {response.json()}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"{moeda} failed: {e}")

if __name__ == "__main__":
    test_api()
