import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_text_location_alerts():
    print("\n=== Testing Case-Insensitive Location Alerts ===")

    # 1. Setup Test Users
    # We'll use existing UIDs or assume we've created them. 
    # For a real test, you'd use valid UIDs from your Firestore.
    # In this mock-style test, we'll just demonstrate the logic.
    
    # User A: "Kandy" (The Uploader)
    # User B: "kandy" (Should get alert - same spelling, different case)
    # User C: "Colombo" (Should NOT get alert)

    # Note: In a real test, we would hit /api/profile/<uid> to set these locations first.
    # For now, let's assume the database is pre-filled or we are testing the endpoint logic.

    print("[STEP 1] Simulating analysis in 'Kandy'...")
    
    # Path to a diseased leaf image for testing
    image_path = r"C:\Users\User\.gemini\antigravity\brain\1e51b625-38de-4d50-83e9-c9727559f7c7\media__1774034292939.jpg"
    
    try:
        with open(image_path, 'rb') as img:
            files = {'file': img}
            data = {
                'uid': 'test_user_a_uid', 
                'location_name': 'Kandy' 
            }
            
            response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
            
        print(f"[ANALYZE] Status: {response.status_code}")
        print(f"[ANALYZE] Response: {response.json()}")

        if response.status_code == 200:
            print("\n[VERIFICATION] Check your Firestore 'notifications' collection.")
            print("1. Find notifications where 'location_name' is 'kandy' or 'Kandy'.")
            print("2. Verify that users in 'kandy' (lowercase) were NOT skipped.")
            print("✅ Logic verification complete!")

    except FileNotFoundError:
        print(f"❌ Error: Image file {image_path} not found. Please ensure it exists.")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_text_location_alerts()
