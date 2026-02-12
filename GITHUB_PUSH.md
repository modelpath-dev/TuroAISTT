# 📤 Push to GitHub - Quick Guide

Your repository is now initialized and committed! Follow these steps to push to GitHub:

## Option 1: Using GitHub Web Interface (Easiest)

1. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `radiology-voice-to-report` (or your preferred name)
   - Description: "AI-powered radiology voice-to-report system"
   - Choose **Public** or **Private**
   - ⚠️ **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Push your code**:
   ```bash
   # Copy these commands from GitHub (they'll show after creating the repo)
   # Replace YOUR_USERNAME and YOUR_REPO with your actual values
   
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

## Option 2: Using GitHub CLI (If installed)

```bash
# Install GitHub CLI if not already installed
# On Ubuntu/Debian: sudo apt install gh
# On Mac: brew install gh

# Login to GitHub
gh auth login

# Create repo and push
gh repo create radiology-voice-to-report --public --source=. --remote=origin --push
```

## After Pushing

1. **Verify on GitHub**: Visit your repository URL to confirm all files are there

2. **Set up secrets** (for CI/CD later):
   - Go to Settings → Secrets and variables → Actions
   - Add secrets for `OPENAI_API_KEY` and `GOOGLE_API_KEY`

3. **Deploy**:
   - Follow [DEPLOYMENT.md](./DEPLOYMENT.md) to deploy to Railway and Vercel
   - Both platforms can auto-deploy from your GitHub repo

## ⚠️ Important Notes

- Your `.env` file is **NOT** pushed (it's in `.gitignore`)
- Never commit API keys to GitHub
- Use `.env.example` as a template for others
- The `temp_audio/` folder is excluded from git

## Next Steps

After pushing to GitHub:
1. Deploy backend to Railway: https://railway.app
2. Deploy frontend to Vercel: https://vercel.com
3. See [QUICK_START.md](./QUICK_START.md) for deployment steps

---

**Need help?** Check the [README.md](./README.md) for more information.
