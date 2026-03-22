# 🚀 Hosting Teera Backend on Render

This guide explains how to deploy the Teera Flask backend to [Render](https://render.com).

## 📋 Step 0: Connect to Your Git Repository

If your backend code is not yet in Git, follow these steps to connect your local folder to your empty repository:

1. **Open a terminal** (PowerShell or Command Prompt) and go to your backend directory:
   ```bash
   cd d:\TEERA\backend_teera
   ```

2. **Initialize Git & Commit**:
   ```bash
   git init
   git add .
   git commit -m "Initial backend commit"
   ```

3. **Add Remote & Push**:
   Replace `YOUR_REPO_URL` with the one from your Git provider (e.g., https://github.com/username/repo.git).
   ```bash
   git branch -M main
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

## 📋 Step 1: Prepare Your Repository

## 🔒 Step 2: Secure Firebase Configuration

Since `firebase_config.json` contains sensitive credentials, you should **not** commit it to version control. Instead, we use an Environment Variable.

### 1. Convert your JSON to Base64
Run this command in your local terminal (Windows PowerShell) to get the Base64 string:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("d:\TEERA\backend_teera\firebase_config.json"))
```

### 2. Copy the Output
You will use this long string in Step 3.

---

## 🌐 Step 3: Deployment on Render

1. **Log in to Render** and click **New +** > **Web Service**.
2. **Connect your repository**.
3. **Configure the Web Service**:
   - **Name**: `teera-backend`
   - **Language**: `Python`
   - **Branch**: `main` (or your preferred branch)
   - **Build Command**: `pip install -r backend_teera/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend_teera app:app`
   
   > [!NOTE]
   > The `--chdir backend_teera` flag tells Gunicorn to look for `app.py` inside the backend directory.

4. **Add Environment Variables**:
   Click on **Advanced** > **Add Environment Variable**:
   - `FIREBASE_CONFIG_BASE64`: Paste the Base64 string from Step 2.
   - `PYTHON_VERSION`: `3.8.10` (or your local version).

---

## 🔄 Step 4: Update Frontend Configuration

Once your Render service is "Live", you will get a URL like `https://teera-backend.onrender.com`.

1. Go to `Frontend_teera/Teera/Frontend/TeeraApp/src/config.ts`.
2. Update the `BASE_URL` to your new Render URL.

```typescript
export const BASE_URL = 'https://teera-backend.onrender.com';
```

---

## ⚠️ Important Notes

- **Free Tier Sleep**: Render's free tier spins down after 15 minutes of inactivity. The first request after a sleep period may take 30+ seconds to respond.
- **Model Size**: Your ML model (~11MB) is small enough for the free tier, but if it grows significantly, you may need a higher tier or external storage like Cloud Storage.
