import requests

BASE_URL = "http://127.0.0.1:5000"

def test_chat():
    print("Testing /api/chat...")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={"message": "Hi"})
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
        
        if response.status_code == 200:
            print("✅ SUCCESS: Received response from chatbot.")
        else:
            print(f"❌ FAILURE: Status code {response.status_code}")
            
    except Exception as e:
        print("Error during test:", e)

if __name__ == "__main__":
    test_chat()
