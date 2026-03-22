import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin (Assuming the config is in the same directory)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def setup_manual_test_users():
    print("=== Setting up Manual Test Users in Firestore ===")
    
    users = [
        {"uid": "user_kandy_1", "full_name": "Farmer A", "location_name": "Kandy"},
        {"uid": "user_kandy_2", "full_name": "Farmer B", "location_name": "kandy"}, # Test lowercase
        {"uid": "user_colombo_1", "full_name": "Farmer C", "location_name": "Colombo"}, # Test different location
    ]

    for user in users:
        db.collection('users').document(user['uid']).set({
            "full_name": user['full_name'],
            "location_name": user['location_name'],
            "email": f"{user['uid']}@example.com",
            "joined_at": firestore.SERVER_TIMESTAMP
        })
        print(f"Created/Updated {user['full_name']} at {user['location_name']}")

    print("\n✅ Test users are ready in Firestore!")

if __name__ == "__main__":
    setup_manual_test_users()
