# 🚀 Hosting Teera Backend on Vercel

This guide explains how to deploy the Teera Flask backend to [Vercel](https://vercel.com).

## 📋 Step 1: Prepare Your Repository

Ensure your backend directory (`backend_teera/`) contains the `vercel.json` file. This tells Vercel how to handle your Flask application.

### Required Files:
- `app.py`
- `requirements.txt`
- `vercel.json`
- `cinnamon_disease_model.keras/` (ML model weights)

---

## 🔒 Step 2: Secure Firebase Configuration

Just like with Render, we use an Environment Variable for your `firebase_config.json`.

1. **Get your Base64 string** (if you haven't already):
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("d:\TEERA\backend_teera\firebase_config.json"))
   ```

2. **Copy this string** for use in Step 3.

---

## 🌐 Step 3: Deployment on Vercel

1. **Log in to Vercel** and click **Add New** > **Project**.
2. **Import your Git repository**.
3. **Configure Project**:
   - **Framework Preset**: `Other` (Vercel will detect Python automatically).
   - **Root Directory**: `backend_teera`
4. **Environment Variables**:
   Click on **Environment Variables** and add:
   - `FIREBASE_CONFIG_BASE64`: Paste your Base64 string.
5. **Deploy**: Click **Deploy**.

---

## 🔄 Step 4: Update Frontend Configuration

Once deployed, Vercel will give you a URL like `https://teera-backend.vercel.app`.

1. Go to `Frontend_teera/Teera/Frontend/TeeraApp/src/config.ts`.
2. Update the `BASE_URL`:

```typescript
export const BASE_URL = 'https://teera-backend.vercel.app';
```

---

## ⚠️ Important Notes

- **Serverless Limits**: Vercel runs your code as Serverless Functions. Each request has a maximum execution time (usually 10-60 seconds depending on your plan). 
- **Model Loading**: Large ML models might approach the function size limit (250MB). Your ~11MB model is safe.
- **Dynamic Port**: Vercel handles the port automatically; you don't need to specify it.
