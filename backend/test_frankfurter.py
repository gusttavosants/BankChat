import requests

def test_frankfurter():
    url = "https://api.frankfurter.app/latest?from=USD&to=BRL"
    try:
        response = requests.get(url, timeout=5)
        print(f"Frankfurter Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Data: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Frankfurter failed: {e}")

if __name__ == "__main__":
    test_frankfurter()
