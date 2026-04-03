import time
import threading
import random
import math
import uuid
from flask import Flask, request, jsonify, send_from_directory  # type: ignore
from flask_cors import CORS  # type: ignore
import requests  # type: ignore
import io
import os
import numpy as np  # type: ignore
from PIL import Image  # type: ignore
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TF warnings
import tensorflow as tf  # type: ignore
import keras  # type: ignore
import firebase_admin  # type: ignore
from firebase_admin import credentials, firestore, auth, messaging  # type: ignore
from datetime import datetime, timedelta, timezone



# --- INITIALIZATION ---
import base64
import json

# Handle Firebase Config via Environment Variable (for Render/Production)
# OR via local file (for Development)
# Handle Firebase Config via Environment Variable (for Render/Production)
# OR via local file (for Development)
firebase_config_env = os.environ.get("FIREBASE_CONFIG_BASE64")
cred = None

if firebase_config_env:
    try:
        print("Initializing Firebase from environment variable...")
        config_dict = json.loads(base64.b64decode(firebase_config_env).decode('utf-8'))
        cred = credentials.Certificate(config_dict)
    except Exception as e:
        print(f"FAILED to initialize Firebase from environment variable: {e}")

if not cred:
    # Use absolute path to ensure the file is found regardless of where the server starts
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firebase_config.json")
    if os.path.exists(config_path):
        try:
            print(f"Initializing Firebase from local file: {config_path}")
            cred = credentials.Certificate(config_path)
        except Exception as e:
            print(f"ERROR: Failed to load Firebase certificate from {config_path}: {e}")
    else:
        print(f"ERROR: firebase_config.json not found at {config_path}")

if cred:
    try:
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase SDK initialized successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize Firebase app: {e}")
        db = None
else:
    print("WARNING: Firebase will NOT be available (cred is None).")
    db = None

app = Flask(__name__)
CORS(app) 

# Ensure uploads directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    """Health check endpoint for Render/Heroku."""
    return jsonify({
        "status": "Healthy",
        "message": "Teera Backend is online and ready!",
        "version": "1.0.0"
    }), 200

# Twilio removed in favor of Firebase Email Verification

# --- ML MODEL LOADING (LAZY) ---
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cinnamon_disease_model.keras")
disease_model = None
model_initialized = False

def get_disease_model():
    """Lazy model loader to prevent Heroku boot timeout."""
    global disease_model, model_initialized
    if model_initialized:
        return disease_model

    if os.path.exists(MODEL_PATH):
        print(f"Loading ML model from {MODEL_PATH}...")
        try:
            # Load MobileNetV2 base
            base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights=None)
            
            inputs = tf.keras.Input(shape=(224, 224, 3), name='input_layer_1')
            x = base_model(inputs)
            x = tf.keras.layers.GlobalAveragePooling2D(name='global_average_pooling2d')(x)
            x = tf.keras.layers.Dense(128, activation='relu', name='dense')(x)
            x = tf.keras.layers.Dropout(0.2, name='dropout')(x)
            predictions = tf.keras.layers.Dense(2, activation='softmax', name='dense_1')(x)

            disease_model = tf.keras.Model(inputs=inputs, outputs=predictions)

            # Load Weights
            WEIGHTS_PATH = os.path.join(MODEL_PATH, "model.weights.h5")
            if os.path.exists(WEIGHTS_PATH):
                disease_model.load_weights(WEIGHTS_PATH)
                print("ML model weights loaded successfully.")
            else:
                print(f"WARNING: Weights file {WEIGHTS_PATH} not found.")
                disease_model = None

        except Exception as e:
            print(f"FAILED to build or load model: {e}")
            disease_model = None
    else:
        print(f"WARNING: Model directory {MODEL_PATH} not found!")
    
    model_initialized = True
    return disease_model

# Firebase Web API Key (Used for Sign-In with Password)
# You can find this in Firebase Console -> Project Settings -> General -> Web API Key
FIREBASE_WEB_API_KEY = 'AIzaSyD8xyi4veuUY9HWBU0ty1oCnvz7X9buYdc'

# --- BACKGROUND REMINDER TASK ---
def check_and_send_reminders():
    # This thread wakes up every hour to see if any reminders are scheduled for today
    while True:
        try:
            today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            users_stream = db.collection('users').stream()
            
            for user_doc in users_stream:
                user_data = user_doc.to_dict()
                user_ref = user_doc.reference
                
                # Fetch only un-notified reminders for this user
                reminders_query = user_ref.collection('reminders').where('notified', '==', False).stream()
                
                for doc in reminders_query:
                    rem_data = doc.to_dict()
                    
                    if rem_data.get('date') == today_str:
                        fcm_token = user_data.get('fcm_token')
                        
                        if fcm_token:
                            try:
                                message = messaging.Message(
                                    notification=messaging.Notification(
                                        title=f"Reminder: {rem_data.get('name')}",
                                        body=rem_data.get('description', 'You have a scheduled task for today.')
                                    ),
                                    token=fcm_token,
                                )
                                messaging.send(message)
                            except Exception as e:
                                print(f"Firebase Messaging Error for {user_doc.id}: {e}")
                                
                        # Mark as notified whether they have a token or not, so we don't retry forever
                        doc.reference.update({"notified": True})
                        
        except Exception as e:
            print(f"Reminder background task error: {e}")
            
        # Run checks every 1 hour (3600 seconds)
        time.sleep(3600)

reminder_thread = threading.Thread(target=check_and_send_reminders, daemon=True)
reminder_thread.start()


# --- ROUTES ---

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    phone = data.get('phone_number')
    full_name = data.get('full_name')
    password = data.get('password')

    # 1. Check if phone exists
    existing_user = db.collection('users').where('phone_number', '==', phone).limit(1).get()
    if len(existing_user) > 0:
        return jsonify({"message": f"You have already signed up with {phone}."}), 400

    # 2. Sign up to Firebase Auth via REST API to get idToken
    signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    req = requests.post(signup_url, json={"email": email, "password": password, "returnSecureToken": True})
    
    if req.status_code != 200:
        error_msg = req.json().get('error', {}).get('message', 'Signup failed')
        return jsonify({"error": error_msg}), 400
        
    resp_data = req.json()
    uid = resp_data['localId']
    id_token = resp_data['idToken']
    
    # 3. Trigger Firebase Email Verification
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
    verify_req = requests.post(verify_url, json={"requestType": "VERIFY_EMAIL", "idToken": id_token})
    if verify_req.status_code != 200:
        return jsonify({"error": "Failed to send verification email"}), 500

    # 4. Create permanent user document in Firestore immediately
    db.collection('users').document(uid).set({
        "full_name": full_name,
        "email": email,
        "phone_number": phone,
        "preferences": {"mood": "Light", "language": "English"},
        "joined_at": firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({"message": "Verification email sent. Please check your inbox before signing in."}), 200

@app.route('/api/posts', methods=['GET', 'POST'])
def manage_posts():
    if request.method == 'POST':
        try:
            # Handle post text, image, and form data
            uid = request.form.get('uid')
            post_text = request.form.get('postText', '')
            
            if not uid:
                return jsonify({"error": "User UID is required"}), 400

            # 1. Image upload handling
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = f"{uuid.uuid4().hex}_{file.filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    image_url = f"{request.host_url}uploads/{filename}"

            # 2. Fetch User Details for Post
            user_doc = db.collection('users').document(uid).get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            user_name = user_data.get('full_name', 'Unknown User')
            user_handle = f"@{user_name.replace(' ', '').lower()}"
            user_img = user_data.get('profile_photo', 'https://i.pravatar.cc/150')

            # 3. Create Post Document
            post_ref = db.collection('posts').document()
            post_data = {
                "id": post_ref.id,
                "user_uid": uid,
                "userName": user_name,
                "userHandle": user_handle,
                "userImg": user_img,
                "postText": post_text,
                "postImg": image_url,
                "likes": 0,
                "comments": 0,
                "created_at": firestore.SERVER_TIMESTAMP,
                "isVerified": False
            }
            
            # Save to database (accepts the Sentinel)
            post_ref.set(post_data)
            
            # Make response serializable by temporarily removing or converting the Sentinel
            response_data = post_data.copy()
            response_data['created_at'] = datetime.now(timezone.utc).isoformat()
            
            return jsonify({"message": "Post created successfully", "post": response_data}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'GET':
        try:
            # Fetch the most recent 50 posts
            posts_query = db.collection('posts').order_by('created_at', direction=firestore.Query.DESCENDING).limit(50)
            posts = []
            for doc in posts_query.stream():
                data = doc.to_dict()
                
                # Format timestamps for JSON response
                if 'created_at' in data and data['created_at']:
                    # Firestore SERVER_TIMESTAMP is sometimes not evaluated to an object right away, wait,
                    # when we read it back it's a DatetimeWithNanoseconds
                    try:
                        data['created_at'] = data['created_at'].isoformat()
                    except AttributeError:
                        data['created_at'] = str(data['created_at'])
                else:
                    data['created_at'] = ""

                # Compute time ago roughly
                # For simplicity, we can pass the timestamp correctly to frontend and let fontend handle it 
                # or just hardcode passing ISO string, currently formatting it as ISO string.
                # However, the frontend currently expects `time: '2h'` etc. Let's just create a quick formatter.
                data['time'] = "Recently"
                if data.get('created_at'):
                    try:
                        dt = datetime.fromisoformat(data['created_at'])
                        now = datetime.now(timezone.utc)
                        diff = now - dt
                        if diff.days > 0:
                            data['time'] = f"{diff.days}d"
                        elif diff.seconds >= 3600:
                            data['time'] = f"{diff.seconds // 3600}h"
                        elif diff.seconds >= 60:
                            data['time'] = f"{diff.seconds // 60}m"
                        else:
                            data['time'] = "Just now"
                    except:
                        pass
                
                posts.append(data)
                
            return jsonify(posts), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/profile/<uid>', methods=['GET', 'POST'])
def handle_profile(uid):
    user_ref = db.collection('users').document(uid)
    if request.method == 'GET':
        doc = user_ref.get()
        return jsonify(doc.to_dict()) if doc.exists else (jsonify({"error": "User not found"}), 404)

    if request.method == 'POST':
        data = request.json
        update_fields = {}
        
        # 1. Update Name
        if 'full_name' in data:
            update_fields['full_name'] = data['full_name']
            
        # 2. Update Phone Number
        if 'phone_number' in data:
            update_fields['phone_number'] = data['phone_number']
            
        # 3. Update Profile Photo (stores as URL or Base64 string)
        if 'profile_photo' in data:
            update_fields['profile_photo'] = data['profile_photo']

        # 4. Profile Preferences
        if 'mood' in data:
            update_fields['preferences.mood'] = data['mood']
        if 'language' in data:
            update_fields['preferences.language'] = data['language']
            
        # 5. Location Name (e.g. "Kandy", "Colombo")
        if 'location_name' in data:
            update_fields['location_name'] = data['location_name']
            
        # 6. FCM Token for Push Notifications
        if 'fcm_token' in data:
            update_fields['fcm_token'] = data['fcm_token']
            
        # 6. Update Email Address (Requires Auth Update)
        if 'email' in data:
            new_email = data['email']
            try:
                # Update Firebase Authentication email
                auth.update_user(uid, email=new_email)
                update_fields['email'] = new_email
            except Exception as e:
                return jsonify({"error": f"Failed to update Auth email: {str(e)}"}), 400

        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        try:
            user_ref.update(update_fields)
            return jsonify({"message": "Profile updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400



    # Call Firebase Identity Toolkit REST API to verify password
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        req = requests.post(url, json=payload)
        resp_data = req.json()
        
        if req.status_code == 200:
            uid = resp_data.get('localId')
            
            # Check if email is verified
            user_record = auth.get_user(uid)
            if not user_record.email_verified:
                return jsonify({"error": "Please verify your email before signing in."}), 403
                
            id_token = resp_data.get('idToken')
            return jsonify({
                "message": "Signed in successfully",
                "uid": uid,
                "idToken": id_token
            }), 200
        else:
            error_message = resp_data.get('error', {}).get('message', 'Unknown Error')
            return jsonify({"error": error_message}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_disease_broadcast(loc_name, uploader_uid):
    if not loc_name:
        return 0
        
    loc_name_lower = loc_name.strip().lower()
    
    users_ref = db.collection('users')
    all_users = users_ref.stream()
    
    batch = db.batch()
    notifications_created = 0
    
    for user_doc in all_users:
        if user_doc.id == uploader_uid:
            continue # Don't alert the person who just uploaded it
            
        user_data = user_doc.to_dict()
        user_loc = user_data.get('location_name')
        
        if user_loc and user_loc.strip().lower() == loc_name_lower:
            # Create a notification in Firestore
            notif_ref = db.collection('notifications').document()
            batch.set(notif_ref, {
                "user_uid": user_doc.id,
                "type": "disease_alert",
                "title": "Disease Alert in Your Area",
                "message": f"Rough Bark Disease was detected in {user_loc}. Please check your plants.",
                "location_name": user_loc,
                "created_at": firestore.SERVER_TIMESTAMP,
                "read": False
            })
            
            # Trigger FCM Push Notification
            fcm_token = user_data.get('fcm_token')
            if fcm_token:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title="Disease Alert in Your Area",
                            body=f"Rough Bark Disease was detected in {user_loc}. Please check your plants."
                        ),
                        token=fcm_token,
                    )
                    messaging.send(message)
                except Exception as e:
                    print(f"Failed to send FCM to {user_doc.id}: {e}")
                    
            notifications_created += 1
    
    if notifications_created > 0:
        batch.commit()
    
    return notifications_created

@app.route('/api/analyze', methods=['POST'])
def analyze_leaf():
    current_model = get_disease_model()
    if not current_model:
        return jsonify({"error": "ML model is not loaded on the server."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 1. Read the image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        
        # 2. Resize to 224x224 (required by MobileNetV2)
        img = img.resize((224, 224))
        
        # 3. Convert to numpy array and preprocess
        img_array = np.array(img)
        # MobileNetV2 uses preprocess_input which maps 0-255 to -1 to 1
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        # Add batch dimension
        img_batch = np.expand_dims(img_array, axis=0)
        
        # 4. Predict
        try:
            predictions = disease_model.predict(img_batch, verbose=0)
        except Exception as e:
            print(f"Inference error: {e}")
            return jsonify({"error": f"Model inference failed: {str(e)}"}), 500
        
        # The output is [1, 2] probability array
        confidence_scores = predictions[0]
        predicted_class_idx = int(np.argmax(confidence_scores))
        confidence_percentage = float(np.max(confidence_scores)) * 100
        
        # 5. Map to UI format
        # Index 0 = Healthy, Index 1 = Rough Bark Disease
        if predicted_class_idx == 0:
            result = {
                "diagnosis": "Healthy",
                "confidence": f"{int(confidence_percentage)}%",
                "severity": "None",
                "description": "The leaf appears healthy with no visible signs of disease."
            }
        else:
            result = {
                "diagnosis": "Rough Bark Disease",
                "confidence": f"{int(confidence_percentage)}%",
                "severity": "Medium",
                "description": "Early symptoms of bark cracking or infection observed. Recommended to isolate the plant and treat accordingly."
            }
            
            # Extract location and uploader info from form data
            loc_name = request.form.get('location_name')
            uploader_uid = request.form.get('uid')
            
            # Use the new helper function for broadcasting
            if loc_name:
                send_disease_broadcast(loc_name, uploader_uid)
            
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/broadcast', methods=['POST'])
def manual_broadcast():
    data = request.json
    city = data.get('city')
    disease = data.get('disease', 'Rough Bark Disease')
    uid = data.get('uid')
    
    if not city:
        return jsonify({"error": "City name is required"}), 400
        
    try:
        count = send_disease_broadcast(city, uid)
        return jsonify({
            "message": f"Broadcast successful. {count} users alerted in {city}.",
            "count": count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Notifications page 

@app.route('/api/notifications/<uid>', methods=['GET'])
def get_notifications(uid):
    try:
        notifs_ref = db.collection('notifications')
        # Fetch without order_by to avoid needing a composite index
        query = notifs_ref.where('user_uid', '==', uid).limit(50)
        docs = query.stream()
        
        notifications = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            notifications.append(data)
            
        # Sort in Python by 'created_at' descending (newest first)
        notifications.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
            
        # Format timestamps for JSON response
        for n in notifications:
            if 'created_at' in n and n['created_at']:
                try:
                    n['created_at'] = n['created_at'].isoformat()
                except AttributeError:
                    n['created_at'] = str(n['created_at'])

        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# calender and reminders
@app.route('/api/reminders', methods=['POST'])
def save_reminder():
    data = request.json
    uid = data.get('uid')
    reminder_name = data.get('reminder_name')
    description = data.get('description')
    date = data.get('date') # Expected in ISO format or YYYY-MM-DD

    if not all([uid, reminder_name, date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        reminder_ref = db.collection('users').document(uid).collection('reminders').document()
        reminder_ref.set({
            "name": reminder_name,
            "description": description or "",
            "date": date,
            "created_at": firestore.SERVER_TIMESTAMP,
            "notified": False
        })
        return jsonify({"message": "Reminder saved successfully", "id": reminder_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-reminders/<uid>', methods=['GET'])
def get_reminders(uid):
    try:
        reminders_ref = db.collection('users').document(uid).collection('reminders')
        # Order by date so the most recent ones appear first in "Upcoming Tasks"
        docs = reminders_ref.order_by('date').stream()
        
        reminders_list = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            reminders_list.append(data)
            
        return jsonify(reminders_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '')
    
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400
        
    try:
        import urllib.parse
        encoded_msg = urllib.parse.quote(user_msg)
        api_url = f"https://api.popcat.xyz/chatbot?msg={encoded_msg}&owner=Teera&botname=TeeraBot"
        
        # Added timeout to prevent hanging the server
        response = requests.get(api_url, timeout=7)
        
        if response.status_code == 200:
            bot_reply = response.json().get('response', 'Sorry, I could not understand that.')
            return jsonify({"reply": bot_reply}), 200
        else:
            # Fallback to local rules if API is unreachable
            raise Exception("API status not 200")
            
    except Exception as e:
        # --- Local Rule-Based Fallback ---
        msg_lower = user_msg.lower()
        
        # Simple keyword-based responses for plant care
        if any(kw in msg_lower for kw in ['hi', 'hello', 'hey', 'ayubowan']):
            reply = "Ayubowan! I'm Teera. How can I help you with your plants today?"
        elif any(kw in msg_lower for kw in ['water', 'watering']):
            reply = "Most plants prefer the soil to be moist but not soggy. Check the top inch of soil; if it's dry, it's time to water!"
        elif any(kw in msg_lower for kw in ['disease', 'sick', 'leaf', 'spot']):
            reply = "If you notice spots or yellowing, use my 'Scan' feature! It can identify common diseases like Rough Bark Disease."
        elif any(kw in msg_lower for kw in ['cinnamon', 'tree']):
            reply = "Cinnamon trees thrive in wet, tropical climates with plenty of sunlight and well-drained soil."
        elif any(kw in msg_lower for kw in ['sunlight', 'sun', 'light']):
            reply = "Most indoor plants need bright, indirect sunlight. If leaves are turning brown, they might be getting too much direct sun."
        else:
            reply = "I'm having a little trouble connecting to my AI brain, but I'm here to help! Try asking about 'watering', 'sunlight', or use the 'Scan' feature to check for diseases."
            
        return jsonify({"reply": reply}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    # In a stateless Firebase system, logout is mostly handled by the frontend 
    # (deleting the ID token). This endpoint exists to provide a clear logout sign-off.
    return jsonify({"message": "Successfully logged out"}), 200


if __name__ == '__main__':
    # Use PORT from environment variable (required by Render) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


