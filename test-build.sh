#!/bin/bash

echo "🚀 Testing Frontend Build..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the frontend
echo "🔨 Building frontend..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
    echo "📁 Build output in: frontend/dist"
else
    echo "❌ Frontend build failed!"
    exit 1
fi

cd ..

echo ""
echo "✅ All checks passed!"
echo ""
echo "Next steps:"
echo "1. Deploy backend to Railway/Render (see DEPLOYMENT.md)"
echo "2. Update frontend/.env.production with backend URL"
echo "3. Deploy frontend to Vercel"
