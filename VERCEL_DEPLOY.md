# 🚀 Frontend Deployment to Vercel

**Backend URL**: `http://46.224.57.116:8082` (Configured!)

## Step 1: Push Latest Changes

I've already pushed the configuration to GitHub.

## Step 2: Deploy to Vercel

1. **Go to [vercel.com](https://vercel.com/new)**
2. **Import your repository**: `modelpath-dev/TuroAISTT`
3. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (⚠️ Important!)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. **Environment Variables**:
   Add this one variable:
   ```
   VITE_API_URL = http://46.224.57.116:8082
   ```
5. **Click Deploy!**

## Step 3: Important CORS Note ⚠️

Since your backend is on `http` (insecure) and Vercel is `https` (secure), you might face **Mixed Content** errors.

**Solutions:**
1. **Best**: Configure SSL/HTTPS for your backend (get a domain name)
2. **Quick Fix**: Add this meta tag to `frontend/index.html` (I can do this for you):
   ```html
   <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
   ```
   *(Note: This might not work if the backend doesn't support HTTPS on port 8443 or similar)*

**Recommendation:**
Deploying to a VPS without HTTPS will cause issues with modern browsers. **However, for testing, you can use Vercel.**

If the backend IP supports HTTPS (e.g. `https://46.224.57.116:8082`), use that instead.

---

**Ready to deploy? Go to Vercel and import the repo!**
