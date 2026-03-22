import requests
import random
import time
import firebase_admin
from firebase_admin import credentials, firestore

BASE_URL = "http://127.0.0.1:5000/api"

def setup_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

def test_signup_and_verify(db):
    print("=== Testing 1. Signup & 2. OTP Verification ===")
    
    # Generate random test data
    rand_id = random.randint(100000, 999999)
    email = f"testuser_{rand_id}@example.com"
    phone_number = f"+1555{str(rand_id).zfill(6)}"
    password = f"Pass_{rand_id}!"
    full_name = f"Test User {rand_id}"
    
    # 1. Signup
    print(f"\n[SIGNUP] Testing signup with Email: {email}, Phone: {phone_number}")
    signup_data = {
        "email": email,
        "phone_number": phone_number,
        "full_name": full_name,
        "password": password
    }
    
    resp = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"[SIGNUP] Status Code: {resp.status_code}")
    print(f"[SIGNUP] Response: {resp.json()}")
    assert resp.status_code == 200, "Signup failed!"
    
    # Let Firestore commit the transaction
    time.sleep(2)
    
    # 2. Get OTP from Firebase temp_registrations
    print("\n[FIREBASE] Fetching OTP from Firestore 'temp_registrations' collection...")
    temp_ref = db.collection('temp_registrations').document(email).get()
    if not temp_ref.exists:
        print("[ERROR] Temp registration not found in Firebase.")
        return None
    
    otp = temp_ref.to_dict().get("otp")
    print(f"[FIREBASE] Fetched OTP: {otp}")
    
    # 3. OTP Verification
    print(f"\n[VERIFY-OTP] Testing OTP verification with OTP: {otp}")
    verify_data = {
        "email": email,
        "otp": otp
    }
    resp = requests.post(f"{BASE_URL}/verify-otp", json=verify_data)
    print(f"[VERIFY-OTP] Status Code: {resp.status_code}")
    print(f"[VERIFY-OTP] Response: {resp.json()}")
    assert resp.status_code == 200, "OTP verification failed!"
    
    uid = resp.json().get("uid")
    print(f"[VERIFY-OTP] Successfully authenticated. User UID: {uid}")
    return uid, email, password

def test_profile(uid):
    print(f"\n=== Testing 4. Profile (UID: {uid}) ===")
    
    # Get Original Email
    resp = requests.get(f"{BASE_URL}/profile/{uid}")
    original_email = resp.json().get('email')

    # Update Profile (including Email and Photo)
    rand_id = random.randint(1000, 9999)
    new_email = f"updated_{rand_id}@example.com"
    new_data = {
        "full_name": "Updated Test User",
        "phone_number": "+15550000000",
        "email": new_email,
        "profile_photo": "https://example.com/photo.jpg",
        "mood": "Dark",
        "language": "Spanish"
    }
    print(f"\n[PROFILE-POST] Updating profile fields + EMAIL to: {new_email}")
    resp = requests.post(f"{BASE_URL}/profile/{uid}", json=new_data)
    print(f"[PROFILE-POST] Status Code: {resp.status_code}")
    print(f"[PROFILE-POST] Response: {resp.json()}")
    assert resp.status_code == 200, "POST Profile failed!"
    
    # Verify Update
    print(f"\n[PROFILE-GET] Fetching profile again to verify update...")
    resp = requests.get(f"{BASE_URL}/profile/{uid}")
    data = resp.json()
    print(f"[PROFILE-GET] Response Data: {data}")
    assert data.get("full_name") == "Updated Test User"
    assert data.get("email") == new_email
    assert data.get("profile_photo") == "https://example.com/photo.jpg"
    print("✅ Profile verification success!")
    return new_email

def test_signin(email, password):
    print("\n=== Testing 3. Sign In ===")
    print(f"\n[SIGNIN] Attempting to sign in with Email: {email}")
    signin_data = {
        "email": email,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/signin", json=signin_data)
    print(f"[SIGNIN] Status Code: {resp.status_code}")
    try:
        print(f"[SIGNIN] Response: {resp.json()}")
    except:
        print(f"[SIGNIN] Response Text: {resp.text}")
        
    if resp.status_code == 404:
        print("\n[INFO] Signin API endpoint is missing (404 Not Found). This needs to be implemented in app.py!")

def test_analyze():
    print("\n=== Testing 5. ML Analysis ===")
    from PIL import Image
    import io
    
    # Create a dummy image
    img = Image.new('RGB', (256, 256), color=(73, 109, 137)) # Deliberately not 224x224 to test resizing
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    files = {'file': ('dummy_leaf.jpg', img_byte_arr, 'image/jpeg')}
    print("[ANALYZE] Sending dummy image to /api/analyze...")
    resp = requests.post(f"{BASE_URL}/analyze", files=files)
    
    print(f"[ANALYZE] Status Code: {resp.status_code}")
    try:
        print(f"[ANALYZE] Response: {resp.json()}")
    except:
        print(f"[ANALYZE] Response: {resp.text}")
    assert resp.status_code == 200, "ML Analysis failed!"

if __name__ == "__main__":
    db = setup_firebase()
    
    # 1. Signup & Verification
    result = test_signup_and_verify(db)
    if result:
        uid, email, password = result
        
        # 2. Profile Operations
        test_profile(uid)
        
        # 3. Signin Failure Example
        test_signin(email, password)
        
        # 4. ML Analysis
        test_analyze()
