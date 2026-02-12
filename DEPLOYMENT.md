# Deployment Guide: Radiology Voice-to-Report Application

This guide covers deploying the application using a **hybrid approach**:
- **Backend (FastAPI)**: Railway or Render
- **Frontend (React + Vite)**: Vercel

---

## Prerequisites

- GitHub account (for connecting to deployment platforms)
- Railway or Render account (for backend)
- Vercel account (for frontend)
- API keys: OpenAI, Google Gemini

---

## Part 1: Deploy Backend to Railway

### Option A: Railway (Recommended)

1. **Install Railway CLI** (optional, for CLI deployment):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy via Railway Dashboard**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and use `Procfile`

3. **Set Environment Variables** in Railway Dashboard:
   ```
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=...
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
   ```

4. **Get Your Backend URL**:
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Copy this URL for frontend configuration

### Option B: Render

1. **Deploy via Render Dashboard**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Set Environment Variables** in Render Dashboard:
   ```
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=...
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
   ```

3. **Get Your Backend URL**:
   - Render will provide a URL like: `https://your-app.onrender.com`

---

## Part 2: Deploy Frontend to Vercel

1. **Update `.env.production`**:
   ```bash
   cd frontend
   nano .env.production
   ```
   
   Replace with your Railway/Render backend URL:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```

2. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

3. **Deploy via Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

4. **Set Environment Variable** in Vercel Dashboard:
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     VITE_API_URL = https://your-backend-url.railway.app
     ```

5. **Deploy**:
   - Vercel will auto-deploy on every push to main branch
   - Get your frontend URL: `https://your-app.vercel.app`

---

## Part 3: Update CORS Settings

After getting your Vercel frontend URL, update the backend environment variable:

**On Railway/Render**, update `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

Redeploy the backend if needed.

---

## Part 4: Testing

1. **Test Backend API**:
   ```bash
   curl https://your-backend-url.railway.app/templates
   ```

2. **Test Frontend**:
   - Visit `https://your-frontend.vercel.app`
   - Upload an audio file
   - Verify transcription and report generation work

3. **Check Logs**:
   - **Railway**: Dashboard → Deployments → View Logs
   - **Render**: Dashboard → Logs
   - **Vercel**: Dashboard → Deployments → Function Logs

---

## Troubleshooting

### Backend Issues

**Error: Module not found**
- Check `requirements.txt` has all dependencies
- Redeploy after updating

**Error: CORS policy**
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check no trailing slashes in URLs

**Audio upload fails**
- Railway/Render have file size limits (check their docs)
- For large files, consider using cloud storage (S3, GCS)

### Frontend Issues

**API calls fail**
- Check `VITE_API_URL` in Vercel environment variables
- Verify backend is running: visit backend URL directly

**Build fails**
- Check Node version compatibility
- Run `npm run build` locally first

---

## Local Development

**Backend**:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

---

## Cost Estimates

- **Railway**: Free tier includes 500 hours/month, $5/month for Hobby plan
- **Render**: Free tier available, $7/month for paid plan
- **Vercel**: Free tier for personal projects, unlimited bandwidth

---

## Next Steps

1. Set up custom domain (optional)
2. Configure CI/CD for auto-deployment
3. Set up monitoring and error tracking (Sentry, LogRocket)
4. Add authentication if needed

---

## Support

For issues:
- Railway: [docs.railway.app](https://docs.railway.app)
- Render: [render.com/docs](https://render.com/docs)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
