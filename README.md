# Radiology Voice-to-Report & Data Extraction Engine

A production-grade AI-powered system that converts radiology voice dictations into structured CAP-compliant reports using OpenAI Whisper, LangGraph, and Google Gemini.

## 🎯 Features

- **Voice Transcription**: High-accuracy medical transcription using OpenAI Whisper
- **AI Refinement**: Context-aware transcript refinement with LangGraph workflow
- **Data Extraction**: Automated extraction of structured data from transcripts
- **Interactive Chatbot**: Clinical assistant for real-time verification support
- **Report Generation**: CAP-compliant DOCX report generation
- **Modern UI**: Beautiful React dashboard with step-by-step workflow

## 🏗️ Architecture

- **Backend**: FastAPI + Python
  - OpenAI Whisper for transcription
  - LangGraph for workflow orchestration
  - Google Gemini for LLM processing
  - Python-docx for report generation

- **Frontend**: React + Vite
  - Modern, responsive UI
  - Real-time chat interface
  - Multi-step verification workflow

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key
- Google Gemini API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd stt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Run the backend**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cd backend
   uvicorn main:app --reload
   ```

4. **Run the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Open your browser**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📦 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Quick deployment** (recommended):
- **Backend**: Railway or Render
- **Frontend**: Vercel

See [QUICK_START.md](./QUICK_START.md) for a condensed deployment guide.

## 🔧 Environment Variables

### Backend
```env
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

### Frontend
```env
VITE_API_URL=http://localhost:8000  # Development
VITE_API_URL=https://your-backend.railway.app  # Production
```

## 📁 Project Structure

```
stt/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── services/
│       ├── transcription.py    # Whisper transcription
│       ├── langgraph_engine.py # LangGraph workflow
│       └── report_gen.py       # Report generation
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   └── App.css            # Styles
│   └── package.json
├── CAP templates/
│   └── JSON_Output/           # CAP protocol templates
├── requirements.txt           # Python dependencies
├── Procfile                   # Railway/Render config
└── DEPLOYMENT.md             # Deployment guide
```

## 🧪 Testing

```bash
# Test frontend build
cd frontend
npm run build

# Test backend
cd backend
pytest  # (if tests are added)
```

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues or questions, please open a GitHub issue.
