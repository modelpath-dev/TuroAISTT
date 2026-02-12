# 🐳 Koyeb Deployment Guide

The error you saw (Exit Code 51) happens because Koyeb is trying to use "Buildpacks" which don't have the required system tools (like ffmpeg) or get confused by the project structure.

**The Fix: Switch from "Buildpack" to "Docker"**

### Step-by-Step Fix

1. **Go to your Koyeb Service Settings**
2. **Find the "Build" section**
3. **Change "Build method" from "Buildpack" to "Docker"**
4. **Set Dockerfile path**: `Dockerfile` (should be default)
5. **Set Build context**: `.` (should be default)
6. **Save and Redeploy**

---

## 🛠️ Configuration Details

If you are setting it up from scratch, here is exactly what to enter:

### 1. Build Settings
- **Build Method**: Docker
- **Dockerfile**: `Dockerfile`

### 2. Service Settings
- **Environment Variables**:
  - `OPENAI_API_KEY`: `your-key`
  - `GOOGLE_API_KEY`: `your-key`
  - `ALLOWED_ORIGINS`: `http://localhost:5173` (update later with Vercel URL)
- **Privileged**: No
- **Instance Type**: Nano (Free)
- **Exposed Port**: `8080` (This MUST match the port in the Dockerfile)

---

## 💡 Why this works
By switching to **Docker**, we use the custom `Dockerfile` I created which:
1. Specifically installs **ffmpeg** (needed for audio)
2. Uses **Python 3.11** (stable for ML)
3. Handles the `backend/` subfolder structure correctly

---

## ⚠️ Memory Note
The Koyeb free tier has **512MB RAM**. 
The "base" whisper model uses about 150MB. This should fit, but if it crashes, we might need to use the "tiny" model.

To switch to tiny model (if needed):
Edit `backend/services/transcription.py` line 6:
`def __init__(self, model_name: str = "tiny"):`

---

**Try changing the build method to Docker now! It should build successfully.**
