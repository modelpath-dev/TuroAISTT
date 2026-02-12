# 🚀 Quick Deployment Reference

## Step 1: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select your repository
3. Add environment variables:
   ```
   OPENAI_API_KEY=your-key
   GOOGLE_API_KEY=your-key
   ALLOWED_ORIGINS=http://localhost:5173
   ```
4. Copy your Railway URL: `https://your-app.railway.app`

## Step 2: Update Frontend Config

Edit `frontend/.env.production`:
```env
VITE_API_URL=https://your-app.railway.app
```

## Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub
2. Configure:
   - Root Directory: `frontend`
   - Framework: Vite
3. Add environment variable:
   ```
   VITE_API_URL=https://your-app.railway.app
   ```
4. Deploy!

## Step 4: Update CORS

In Railway, update `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

## ✅ Done!

Visit your Vercel URL and test the application.

---

**Full Guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
