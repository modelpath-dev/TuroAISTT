# 🚀 Deploy to Fly.io

Fly.io is a great free alternative with better Python support and faster cold starts than Render.

## Prerequisites

- Fly.io account (free): https://fly.io/app/sign-up
- Fly CLI installed

---

## Step 1: Install Fly CLI

### Linux/Mac:
```bash
curl -L https://fly.io/install.sh | sh
```

### Windows (PowerShell):
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

---

## Step 2: Login to Fly.io

```bash
fly auth login
```

This will open your browser to authenticate.

---

## Step 3: Launch Your App

From your project directory:

```bash
cd /home/whopper/Music/stt
fly launch --no-deploy
```

**When prompted:**
- App name: `turoai-stt` (or your choice)
- Region: Choose closest to you (e.g., `sin` for Singapore, `iad` for US East)
- PostgreSQL: **No**
- Redis: **No**

This creates `fly.toml` (already created for you).

---

## Step 4: Set Environment Variables (Secrets)

```bash
fly secrets set OPENAI_API_KEY="your-openai-key-here"
fly secrets set GOOGLE_API_KEY="your-google-key-here"
fly secrets set ALLOWED_ORIGINS="http://localhost:5173"
```

---

## Step 5: Deploy!

```bash
fly deploy
```

This will:
1. Build your Docker image
2. Push to Fly.io registry
3. Deploy to your VM
4. Give you a URL like: `https://turoai-stt.fly.dev`

**First deploy takes 3-5 minutes.**

---

## Step 6: Update Frontend

Copy your Fly.io URL and update `frontend/.env.production`:

```env
VITE_API_URL=https://turoai-stt.fly.dev
```

Commit and push:
```bash
git add frontend/.env.production
git commit -m "Update API URL for Fly.io"
git push
```

---

## Step 7: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import `TuroAISTT` repository
3. Root Directory: `frontend`
4. Add environment variable:
   ```
   VITE_API_URL=https://turoai-stt.fly.dev
   ```
5. Deploy!

---

## Step 8: Update CORS

After getting your Vercel URL, update Fly.io secrets:

```bash
fly secrets set ALLOWED_ORIGINS="https://your-frontend.vercel.app,http://localhost:5173"
```

---

## Useful Fly.io Commands

```bash
# View logs
fly logs

# Check status
fly status

# SSH into your app
fly ssh console

# Scale up/down
fly scale count 1

# View dashboard
fly dashboard
```

---

## Free Tier Limits

- ✅ **3 shared-cpu VMs** (256MB RAM each)
- ✅ **160GB bandwidth/month**
- ✅ **3GB persistent storage**
- ⚠️ No credit card needed for free tier

**Your app uses 1GB RAM**, so it fits in the free tier!

---

## Auto-Scaling

Your `fly.toml` is configured to:
- **Auto-stop** after 5 minutes of inactivity
- **Auto-start** on first request (5-10 second cold start)
- Save costs while staying responsive

---

## Troubleshooting

**Build fails:**
```bash
fly logs
```

**App not responding:**
```bash
fly status
fly logs
```

**Need to rebuild:**
```bash
fly deploy --no-cache
```

---

## Cost Comparison

| Platform | Free Tier | Cold Start | Python Control |
|----------|-----------|------------|----------------|
| **Fly.io** | 3 VMs, 160GB | 5-10s | ✅ Excellent |
| Render | 750h/month | 30-60s | ❌ Poor |
| Railway | 500h/month | None | ✅ Good (expired) |

---

**Ready to deploy!** Run `fly launch --no-deploy` to get started.
