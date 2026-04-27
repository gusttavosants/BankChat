import requests

def test_coingecko():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
    try:
        response = requests.get(url, timeout=5)
        print(f"CoinGecko Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Data: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"CoinGecko failed: {e}")

if __name__ == "__main__":
    test_coingecko()
