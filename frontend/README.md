# Medical Chatbot - React Frontend

## Overview
Minimal React web application for the AI-powered medical chatbot system connecting to FastAPI backend.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Backend (Required)
```bash
# In project root directory
cd ..
python -m uvicorn backend_api:app --reload --port 8000
```

### 3. Start Frontend
```bash
npm run dev
```

Visit: `http://localhost:5173`

## Features

### Patient Dashboard
- ✅ AI Chat with medical Q&A
- ✅ Real-time risk assessment
- ✅ Chat history
- ✅ Risk color coding (GREEN/YELLOW/ORANGE/RED)
- ✅ Medical disclaimer

### Doctor Dashboard
- ✅ Patient list and selection
- ✅ Risk summary per patient
- ✅ High-risk alerts
- ✅ Conversation history view

## API Endpoints Used

| Component | Endpoint | Purpose |
|-----------|----------|---------|
| ChatBox | `POST /api/chat/query` | Send messages |
| ChatBox | `GET /api/chat/history/{id}` | Load history |
| PatientDashboard | `GET /api/patient/{id}` | Patient info |
| PatientDashboard | `GET /api/patient/{id}/risk/summary` | Risk stats |
| DoctorDashboard | `GET /api/patient` | List patients |
| DoctorDashboard | `GET /api/chat/history/{id}` | View chats |
| Login | `GET /api/patient` | Patient selection |

## Configuration

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure
```
src/
├── api/
│   └── api.js              # All API calls
├── components/
│   ├── AlertList.jsx       # Alerts widget
│   ├── ChatBox.jsx         # Chat interface
│   ├── MessageBubble.jsx   # Message display
│   └── RiskBadge.jsx       # Risk indicator
├── pages/
│   ├── Login.jsx           # Role selection
│   ├── PatientDashboard.jsx
│   └── DoctorDashboard.jsx
└── App.jsx                 # Router setup
```

## Tech Stack
- React 19.2.0
- Vite 7.2.4
- React Router
- Axios

## Usage

1. Go to `http://localhost:5173`
2. Select **Patient** or **Doctor** role
3. If Patient: Choose patient from list
4. Click Login

## Troubleshooting

**Backend not responding?**
```bash
# Check backend is running
curl http://localhost:8000/health
```

**No patients available?**
```bash
# Register a test patient
curl -X POST http://localhost:8000/api/patient/register \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"TEST_001","name":"Test User","email":"test@test.com","age":30}'
```

## Demo Tips

For hackathon presentations:
1. Pre-register 2-3 test patients
2. Create chat history with mixed risk levels
3. Show patient view first (chat demo)
4. Switch to doctor view (monitoring)
5. Highlight risk alerts feature

## License
MIT
