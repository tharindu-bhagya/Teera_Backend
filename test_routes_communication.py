import requests

BASE_URL = "http://127.0.0.0:5000"
# Try using 127.0.0.1 since the server binds to 0.0.0.0:5000
BASE_URL = "http://127.0.0.1:5000"

def test_analyze_trailing_slash():
    try:
        response = requests.post(f"{BASE_URL}/api/analyze/")
        print("Response for /api/analyze/ :", response.status_code, response.text)
    except Exception as e:
        print("Error on /api/analyze/ :", e)

def test_analyze_no_slash():
    try:
        response = requests.post(f"{BASE_URL}/api/analyze")
        print("Response for /api/analyze :", response.status_code, response.text)
    except Exception as e:
        print("Error on /api/analyze :", e)

if __name__ == "__main__":
    print("Testing communication...")
    test_analyze_trailing_slash()
    test_analyze_no_slash()
 