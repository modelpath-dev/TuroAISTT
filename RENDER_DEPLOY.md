# 🚀 Deploy to Render (Free Alternative to Railway)

## Why Render?
- ✅ **750 hours/month free** (enough for 24/7 operation)
- ✅ **No credit card required**
- ✅ Auto-deploy from GitHub
- ✅ Easy environment variable management
- ⚠️ Spins down after 15 min inactivity (30-60s cold start)

---

## Quick Deploy Steps

### 1. Sign Up for Render
- Go to [render.com](https://render.com)
- Sign up with your GitHub account (free)

### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `modelpath-dev/TuroAISTT`
3. Render will auto-detect the `render.yaml` configuration

### 3. Configure (if not using render.yaml)
If Render doesn't auto-detect, manually configure:

- **Name**: `turoai-backend`
- **Region**: Oregon (or closest to you)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: Python 3
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- **Plan**: Free

### 4. Add Environment Variables
In Render dashboard, add these environment variables:

```
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-gemini-key
ALLOWED_ORIGINS=http://localhost:5173
```

### 5. Deploy!
- Click **"Create Web Service"**
- Render will build and deploy (takes 2-3 minutes)
- Copy your Render URL: `https://turoai-backend.onrender.com`

---

## Update Frontend

Edit `frontend/.env.production`:
```env
VITE_API_URL=https://turoai-backend.onrender.com
```

Commit and push:
```bash
git add frontend/.env.production render.yaml
git commit -m "Add Render config and update API URL"
git push
```

---

## Deploy Frontend to Vercel

Same as before:
1. Go to [vercel.com](https://vercel.com)
2. Import `TuroAISTT`
3. Root Directory: `frontend`
4. Add env var: `VITE_API_URL=https://turoai-backend.onrender.com`
5. Deploy!

---

## Update CORS

After getting Vercel URL, update Render environment variable:
```
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

---

## ⚠️ Important: Cold Starts

Render free tier spins down after 15 minutes of inactivity. First request after spin-down takes 30-60 seconds.

**Solutions:**
1. **Accept it** - Fine for demo/testing
2. **Keep-alive service** - Use cron-job.org to ping every 14 minutes
3. **Upgrade to paid** - $7/month for always-on

---

## Alternative: Fly.io

If you prefer Fly.io, I can create a `fly.toml` config. It has better cold start times but requires CLI setup.

---

## Comparison

| Platform | Free Tier | Cold Starts | Setup |
|----------|-----------|-------------|-------|
| **Render** | 750h/month | 30-60s | Easiest |
| **Fly.io** | 3 VMs | 5-10s | Medium |
| **Google Cloud Run** | 2M requests | Minimal | Complex |
| **Railway** | 500h/month | None | Easy (expired) |

---

**Recommendation**: Use **Render** for the easiest free deployment!
