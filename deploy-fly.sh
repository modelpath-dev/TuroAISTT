#!/bin/bash

echo "🚀 Fly.io Deployment Script"
echo "=============================="
echo ""

# Check if flyctl is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI not found!"
    echo ""
    echo "Install it with:"
    echo "  curl -L https://fly.io/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ Fly CLI found"
echo ""

# Check if logged in
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io..."
    fly auth login
fi

echo ""
echo "📋 Deployment Steps:"
echo "1. Launch app (creates fly.toml)"
echo "2. Set secrets (API keys)"
echo "3. Deploy!"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Launch (no deploy yet)
echo ""
echo "🚀 Launching app..."
fly launch --no-deploy

# Set secrets
echo ""
echo "🔐 Setting secrets..."
echo "Enter your OPENAI_API_KEY:"
read -s OPENAI_KEY
fly secrets set OPENAI_API_KEY="$OPENAI_KEY"

echo "Enter your GOOGLE_API_KEY:"
read -s GOOGLE_KEY
fly secrets set GOOGLE_API_KEY="$GOOGLE_KEY"

fly secrets set ALLOWED_ORIGINS="http://localhost:5173"

# Deploy
echo ""
echo "🚀 Deploying..."
fly deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Your app URL:"
fly status | grep "Hostname"
echo ""
echo "Next steps:"
echo "1. Copy your app URL"
echo "2. Update frontend/.env.production with the URL"
echo "3. Deploy frontend to Vercel"
