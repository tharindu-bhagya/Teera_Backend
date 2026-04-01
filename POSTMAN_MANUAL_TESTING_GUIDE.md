# Manual Testing Guide with Postman

This guide will walk you through the process of manually testing the Teera Backend APIs using Postman.

## Prerequisites
1. **Postman**: Ensure you have Postman installed. If not, download it from [postman.com/downloads](https://www.postman.com/downloads/).
2. **Backend Server Status**: Make sure your local Flask server is running on `http://127.0.0.1:5000`. You can start it via `python app.py` or `flask run` in the backend directory.

---

## 1. Import the Postman Collection
A pre-configured Postman Collection JSON file has been created to speed up testing.
1. Open Postman.
2. In the top-left corner, click the **Import** button.
3. Select **File**, and locate `Teera_Backend_Postman_Collection.json` inside your `d:\TEERA\backend_teera\` directory.
4. Click **Import**. You will now see a collection named "Teera Backend API" in your workspace.

---

## 2. Set Up Variables
The collection uses Postman Variables to avoid copying and pasting your `uid` everywhere.

1. Click on the imported collection **"Teera Backend API"** on the left sidebar.
2. Go to the **Variables** tab.
3. Keep the `base_url` set to `http://127.0.0.1:5000` (or update it if your server runs elsewhere).
4. Leave `uid` and `idToken` empty for now. We will set them after signing in.

---

## 3. Step-by-Step Testing Walkthrough

Follow exactly this order to test full functionality:

### Step 1: Authentication (`Signup` & `Signin`)
1. **User Signup**:
   - Go to `1. Authentication` > `User Signup`.
   - In the **Body** tab, change the email to something new (e.g., `tester99@test.com`) and phone to a fresh phone number.
   - Click **Send**.
   - *Expected Output:* `200 OK` with "Verification email sent..." message.
   - *(Note: Since Firebase email verification is enabled, signing in immediately may return a 403 Forbidden until you click the link in your email. If you need to test quickly, you may need to use a pre-verified account or manually mark it verified in the Firebase console).*

2. **User Signin**:
   - Go to `User Signin`.
   - Update the **Body** with your existing verified user's email and password.
   - Click **Send**.
   - *Expected Output:* `200 OK` returning `uid` and `idToken`.
   - **Important Action:** Copy the `uid` from the response. Go to the Collection **Variables** tab, paste it into the **Current Value** for `uid`, and click **Save**. Now, all other endpoints will automatically use this `uid`!

### Step 2: User Profile (`Get` & `Update`)
1. **Get User Profile**:
   - Go to `2. User Profile` > `Get User Profile`.
   - Notice the URL says `{{base_url}}/api/profile/{{uid}}`. It knows your UID!
   - Click **Send**. You should see your profile details.
2. **Update User Profile**:
   - Go to `Update User Profile`.
   - In the **Body**, change details like "location_name". Click **Send**.
   - Output: `200 OK` "Profile updated successfully". Run the GET request again to verify changes.

### Step 3: Social Feed (`Create` & `Get`)
1. **Create Post**:
   - Go to `4. Social Feed` > `Create Post`.
   - Go to the **Body** tab (it uses `form-data`).
   - If you want to test image upload, hover over the `image` key, change its type to **File**, and "Select Files" from your PC.
   - Click **Send**. Check for `201 Created`.
2. **Get Posts**:
   - Go to `Get Posts` and click **Send**. Your new post (and any older posts) will appear.

### Step 4: ML Image Analysis (Cinnamon Leaf)
1. **Analyze Image**:
   - Go to `3. Cinnamon Leaf Analysis` > `Analyze Image`.
   - Go to the **Body** tab.
   - In the `file` row, click "Select Files" and pick an image of a leaf from your computer.
   - Click **Send**. The response might take a few seconds and will return a diagnosis (e.g., Healthy/Diseased).

### Step 5: Reminders
1. **Save a Reminder**:
   - Go to `6. Reminders` > `Save a Reminder`.
   - In the **Body**, set a future `date` (YYYY-MM-DD format). Click **Send**.
   - You should get a `201 Created` with the document ID.
2. **Get Reminders**:
   - Go to `Get Reminders` and click **Send**. You'll see an array of your scheduled tasks.

### Step 6: Test Remaining Endpoints
- Connect to `7. TeeraBot Chat` and send a message "Hello". You should get a reply.
- Connect to `5. Notifications` to see if your leaf scan triggered any disease alerts (if the leaf was marked Diseased and location matched).
- Connect to `1. Authentication` > `Logout`.

---

## Understanding The Responses

- **Status 200/201 (Green)**: Your request was successful. The backend functions as intended.
- **Status 400 (Bad Request)**: The JSON you sent is missing required fields or has bad formatting.
- **Status 500 (Internal Server)**: The backend code crashed. Check your Python terminal `app.py` for the exact error traceback.
