# Teera App Backend API Documentation

Base URL: `http://<your-server-ip>:5000` (or `http://localhost:5000` for local development)

## Authentication

### 1. User Signup
Registers a new user with Firebase Authentication and creates a user profile in Firestore. Sends a verification email.
*   **Endpoint:** `/api/signup`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
      "email": "user@example.com",
      "phone_number": "+1234567890",
      "full_name": "John Doe",
      "password": "securepassword123"
    }
    ```
*   **Responses:**
    *   `200 OK`: `{"message": "Verification email sent. Please check your inbox before signing in."}`
    *   `400 Bad Request`: `{"message": "You have already signed up with <phone>."}` (or Firebase errors)

### 2. User Sign-in
Logs in an existing user using email and password via Firebase Identity Toolkit.
*   **Endpoint:** `/api/signin`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword123"
    }
    ```
*   **Responses:**
    *   `200 OK`:
        ```json
        {
          "message": "Signed in successfully",
          "uid": "firebase_user_id_here",
          "idToken": "jwt_token_here"
        }
        ```
    *   `400 Bad Request`: `{"error": "Email and password are required"}`
    *   `401 Unauthorized`: Firebase error messages
    *   `403 Forbidden`: `{"error": "Please verify your email before signing in."}`

### 3. Logout
A stateless placeholder endpoint for logout. To fully log out, the client should clear the auth tokens locally.
*   **Endpoint:** `/api/logout`
*   **Method:** `POST`
*   **Responses:**
    *   `200 OK`: `{"message": "Successfully logged out"}`

---

## User Profile

### 4. Get User Profile
Retrieves user information from Firestore.
*   **Endpoint:** `/api/profile/<uid>`
*   **Method:** `GET`
*   **Responses:**
    *   `200 OK`:
        ```json
        {
          "full_name": "John Doe",
          "email": "user@example.com",
          "phone_number": "+1234567890",
          "location_name": "Colombo",
          "preferences": {"mood": "Light", "language": "English"},
          ...
        }
        ```
    *   `404 Not Found`: `{"error": "User not found"}`

### 5. Update User Profile
Updates specific fields of the user profile.
*   **Endpoint:** `/api/profile/<uid>`
*   **Method:** `POST`
*   **Request Body (JSON):** *(Only include the fields you want to update)*
    ```json
    {
      "full_name": "Jane Doe",
      "phone_number": "+0987654321",
      "profile_photo": "base64_string_or_url",
      "mood": "Dark",
      "language": "Spanish",
      "location_name": "Kandy",
      "fcm_token": "firebase_cloud_messaging_token",
      "email": "new.email@example.com"
    }
    ```
*   **Responses:**
    *   `200 OK`: `{"message": "Profile updated successfully"}`
    *   `400 Bad Request`: `{"error": "No fields to update"}` or Firebase errors when updating email.

---

## Cinnamon Leaf Analysis

### 6. Analyze Leaf Image (ML Model)
Analyzes an image to determine if the cinnamon leaf has "Rough Bark Disease". If disease is detected, alerts others nearby who have the same `location_name`.
*   **Endpoint:** `/api/analyze`
*   **Method:** `POST`
*   **Content-Type:** `multipart/form-data`
*   **Form Data:**
    *   `file` (Required): The image file (jpeg/png).
    *   `location_name` (Optional): The user's location (e.g., "Colombo"). Used for broad-casting disease alerts.
    *   `uid` (Optional): The uploader's Firebase User ID.
*   **Responses:**
    *   `200 OK`:
        ```json
        {
          "diagnosis": "Healthy", // or "Rough Bark Disease"
          "confidence": "98%",
          "severity": "None", // or "Medium"
          "description": "The leaf appears healthy..."
        }
        ```
    *   `400 Bad Request`: Missing file part or selected file.
    *   `500 Internal Server Error`: `{"error": "ML model is not loaded on the server."}`

---

## Notifications

### 7. Get User Notifications
Fetches notifications for a user (e.g., Disease Alerts in their area).
*   **Endpoint:** `/api/notifications/<uid>`
*   **Method:** `GET`
*   **Responses:**
    *   `200 OK`:
        ```json
        [
          {
            "id": "doc_id",
            "type": "disease_alert",
            "title": "Disease Alert in Your Area",
            "message": "Rough Bark Disease was detected in Colombo. Please check your plants.",
            "location_name": "Colombo",
            "read": false,
            "created_at": "2023-10-27T10:30:00.000000+00:00"
          }
        ]
        ```

---

## Calendar and Reminders

### 8. Save a New Reminder
Schedules a task/reminder. The server runs a background job to send an FCM push notification on the scheduled date.
*   **Endpoint:** `/api/reminders`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
      "uid": "firebase_user_id_here",
      "reminder_name": "Water Plants",
      "description": "Don't forget to water the indoor plans",
      "date": "2023-10-27"
    }
    ```
*   **Responses:**
    *   `201 Created`: `{"message": "Reminder saved successfully", "id": "doc_id"}`
    *   `400 Bad Request`: `{"error": "Missing required fields"}`

### 9. Get User Reminders
Fetches all scheduled reminders for the specified user, ordered by date.
*   **Endpoint:** `/api/get-reminders/<uid>`
*   **Method:** `GET`
*   **Responses:**
    *   `200 OK`:
        ```json
        [
          {
            "id": "doc_id",
            "name": "Water Plants",
            "description": "Don't forget to water the indoor plans",
            "date": "2023-10-27",
            "notified": false,
            ...
          }
        ]
        ```

---

## TeeraBot Chat (AI)

### 10. AI Chat Interaction
Sends a message to the Popcat generic AI Chatbot API and returns its response.
*   **Endpoint:** `/api/chat`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
      "message": "Hello, how to grow cinnamon?"
    }
    ```
*   **Responses:**
    *   `200 OK`: `{"reply": "I am TeeraBot, I am here to help you! Cinnamon needs a warm and humid environment..."}`
    *   `400 Bad Request`: `{"error": "No message provided"}`
    *   `500 Internal Server Error`: `{"error": "Failed to reach AI service"}`
