# Medical Chatbot - Post-Discharge Neurological Monitoring

_All project markdown files now live under this docs/ directory. Older reports and status notes are kept in docs/archive/._

## Overview

An AI-powered medical chatbot for post-discharge neurological patient monitoring using Retrieval-Augmented Generation (RAG). The system combines:

- **React + Vite Frontend**: Modern patient dashboard with authentication
- **FastAPI Backend**: RESTful API with dual vector store architecture
- **RAG Engine**: Groq LLM + MiniLM embeddings for intelligent responses
- **Dual Knowledge Base**:
  - Shared medical neurology books/guidelines
  - Patient-specific medical records (private, per-patient)

## Key Features

- 🔐 **Role-Based Authentication**: Patient, Doctor, Nurse roles
- 📄 **Document Upload**: PDF/text medical reports with automatic processing
- 💬 **Structured Questioning**: 3-6 symptom questions per session
- 🎯 **Risk Assessment**: LOW/MEDIUM/HIGH with actionable recommendations
- 🔒 **Privacy**: Patient-specific vector stores, isolated data
- 🚀 **Production-Ready**: FastAPI backend, React frontend

## Architecture

### Upload-First Flow
1. **Login** → Patient authenticated
2. **Upload Medical Reports** → Required before questioning
3. **Daily Check-in** → AI asks 3-6 neurological symptom questions
4. **Risk Assessment** → JSON response with level, reason, action

### Vector Store Strategy
- `vector store/shared/` - System-wide medical knowledge (read-only)
- `vector store/patient_{id}/` - Private patient records
- Both queried simultaneously via RAG for context-aware responses

## Prerequisites

- **Python 3.10-3.13**: Tested on Python 3.14 (warnings expected)
- **Node.js 18+**: For React frontend
- **GROQ API Key**: Get from groq.com

## Quick Start

### 1) Clone
```bash
git clone https://github.com/thamarai-guna/Med-chatbot.git
cd Med-chatbot
```

### 2) Backend Setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Environment
```env
# .env
GROQ_API_KEY=your_groq_api_key_here
```

### 4) Build Shared Vector Store (first time only)
```bash
# Put medical books in Document-pdfs/
python system_loader.py
```

### 5) Run Backend
```bash
uvicorn backend_api:app --reload
```
Backend: http://127.0.0.1:8000

### 6) Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

### 7) Login
- patient1 / pass123
- doctor1 / pass123
- nurse1 / pass123

## Project Structure
```
Med-chatbot/
├── backend_api.py
├── rag_engine.py
├── patient_manager.py
├── system_loader.py
├── falcon.py
├── requirements.txt
├── .env.example
├── Document-pdfs/
├── vector store/
│   ├── shared/
│   └── patient_*/
├── patient_records/
├── frontend/
└── docs/
    ├── README.md
    ├── COLLABORATION.md
    └── frontend.md
```

## API Docs
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Key Endpoints
- POST /api/auth/login
- POST /api/chat/query
- GET /api/chat/history/{patient_id}
- DELETE /api/chat/history/{patient_id}
- POST /api/documents/patient/{patient_id}/upload
- GET /api/patient/{patient_id}/risk/summary

## Troubleshooting
- `sentence_transformers` import: `pip install --force-reinstall sentence-transformers==3.0.1 packaging==25.0`
- Missing vector store: `python system_loader.py`
- Missing GROQ_API_KEY: set in .env
- Port in use: change uvicorn port or Vite port in vite.config.js

