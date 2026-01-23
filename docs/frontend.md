# Medical Chatbot - React Frontend

## Overview
Minimal React web application for the AI-powered medical chatbot system connecting to FastAPI backend.

## Quick Start
```bash
npm install
npm run dev
```
Backend required: run from project root `uvicorn backend_api:app --reload --port 8000`

Visit: http://localhost:5173

## Features
- Patient dashboard: chat, risk assessment, history
- Doctor dashboard: patient list, risk summary, alerts
- Nurse dashboard: role-based access

## API Endpoints Used
| Component | Endpoint | Purpose |
|-----------|----------|---------|
| ChatBox | POST /api/chat/query | Send messages |
| ChatBox | GET /api/chat/history/{id} | Load history |
| PatientDashboard | GET /api/patient/{id} | Patient info |
| PatientDashboard | GET /api/patient/{id}/risk/summary | Risk stats |
| DoctorDashboard | GET /api/patient | List patients |
| DoctorDashboard | GET /api/chat/history/{id} | View chats |
| Login | GET /api/patient | Patient selection |

## Configuration
`frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Structure
```
src/
├── api/
├── components/
├── pages/
└── App.jsx
```

## Troubleshooting
- Backend not responding: `curl http://localhost:8000/health`
- No patients: register via POST /api/patient/register

## License
MIT
