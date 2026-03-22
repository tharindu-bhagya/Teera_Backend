# Teera Backend

This is the Flask-based backend for the Teera application, providing APIs for user authentication, community posts, plant disease analysis, and notifications.

## 🚀 Features

- **User Authentication**: Secure signup and signin using Firebase Auth.
- **Disease Analysis**: ML-powered plant disease detection using TensorFlow/MobileNetV2.
- **Community Feed**: Post management with image uploads and Firestore integration.
- **Real-time Notifications**: Disease alerts and task reminders via Firebase Cloud Messaging (FCM).
- **Chatbot**: Intelligent plant care assistance.

---

## 🛠️ Setup & Installation

### 1. Prerequisites

- **Python 3.8+** installed on your system.
- **Firebase Project**:
  - `firebase_config.json`: Download your service account key from Firebase Console and place it in this directory.
  - **Web API Key**: Ensure the `FIREBASE_WEB_API_KEY` in `app.py` matches your project's Web API Key.
- **ML Model**: Ensure the model weights are located at `cinnamon_disease_model.keras/model.weights.h5`.

### 2. Virtual Environment Setup

It is highly recommended to use a virtual environment to manage dependencies.

```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages using the provided `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

## 🏃 Running the Server

### Manual Startup

You can start the Flask server directly from the `backend_teera` directory:

```powershell
python app.py
```
The server will run on `http://localhost:5000` by default.

### Automated Startup (Recommended)

From the project root (`TEERA/`), you can use the `start_servers.py` script to start both the backend and frontend simultaneously. This script also automatically updates the frontend configuration with your local IP address.

```powershell
python start_servers.py
```

---

## 📁 Directory Structure

- `app.py`: Main Flask application and API endpoints.
- `requirements.txt`: List of Python dependencies.
- `firebase_config.json`: Firebase service account credentials.
- `cinnamon_disease_model.keras/`: Directory containing the ML model weights.
- `uploads/`: Directory where user-uploaded post images are stored.
- `venv/`: Python virtual environment.

---

## 📝 API Documentation

For a detailed list of available API endpoints and their usage, please refer to [API_DOCUMENTATION.md](API_DOCUMENTATION.md).
