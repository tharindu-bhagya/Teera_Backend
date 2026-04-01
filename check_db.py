
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def check_users():
    if os.path.exists("firebase_config.json"):
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        users_ref = db.collection('users')
        docs = users_ref.limit(5).get()
        
        print(f"Total users found (limit 5): {len(docs)}")
        all_keys = set()
        for doc in docs:
            all_keys.update(doc.to_dict().keys())
        print(f"Unique keys in 'users' collection: {list(all_keys)}")
    else:
        print("firebase_config.json NOT FOUND")

if __name__ == "__main__":
    check_users()
