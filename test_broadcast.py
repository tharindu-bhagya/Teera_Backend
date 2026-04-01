import requests
import json

# Replace with your local backend URL and a valid city/UID
BASE_URL = "http://127.0.0.1:5000"
TEST_CITY = "Colombo"
TEST_UID = "test_sender_123"

def test_broadcast():
    url = f"{BASE_URL}/api/broadcast"
    payload = {
        "city": TEST_CITY,
        "disease": "Rough Bark Disease",
        "uid": TEST_UID
    }
    
    print(f"Testing manual broadcast to city: {TEST_CITY}...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Broadcast test passed!")
        else:
            print("❌ Broadcast test failed.")
            
    except Exception as e:
        print(f"Error connecting to backend: {e}")

if __name__ == "__main__":
    test_broadcast()
