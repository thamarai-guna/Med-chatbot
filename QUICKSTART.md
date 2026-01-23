# 🚀 QUICK START GUIDE - Medical Chatbot Demo

## Prerequisites
- Python 3.14+ installed
- Node.js 16+ installed
- Backend dependencies installed (`pip install -r requirements_backend.txt`)

## Step-by-Step Launch

### 1. Start Backend API (Terminal 1)
```powershell
cd C:\Users\tagor\Documents\GitHub\Med-chatbot
python -m uvicorn backend_api:app --reload --port 8000
```

**Wait for:** `Uvicorn running on http://127.0.0.1:8000`

### 2. Start Frontend (Terminal 2)
```powershell
cd C:\Users\tagor\Documents\GitHub\Med-chatbot\frontend
npm run dev
```

**Wait for:** `Local: http://localhost:5173/`

### 3. Open Browser
Navigate to: **http://localhost:5173**

## Demo Flow

### Patient View Demo
1. Click **Patient** role
2. Select any patient from dropdown (e.g., "Test Patient Alpha")
3. Click **Login**
4. Type: "What are the symptoms of diabetes?"
5. Click **Send** → Observe LOW risk response
6. Type: "I have severe chest pain and difficulty breathing"
7. Click **Send** → Observe CRITICAL risk escalation

### Doctor View Demo
1. Click **Logout** (top right)
2. Return to login page
3. Click **Doctor** role
4. Click **Login**
5. Observe alerts panel (shows high-risk patients)
6. Click on "Test Patient Alpha" from patient list
7. View:
   - Risk summary (shows CRITICAL status)
   - Recent conversations
   - Risk distribution statistics

## Troubleshooting

### Backend won't start?
```powershell
# Check if already running
Get-Process | Where-Object {$_.ProcessName -like '*python*'}

# Kill if needed
Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process
```

### No patients available?
```powershell
# Register a test patient via API
curl -X POST http://localhost:8000/api/patient/register `
  -H "Content-Type: application/json" `
  -d '{"patient_id":"DEMO_001","name":"Demo Patient","email":"demo@test.com","age":35}'
```

### Frontend shows CORS error?
- Verify backend is running on port 8000
- Check `frontend/.env` has correct URL
- Restart both backend and frontend

## System Check

### Verify Backend
```powershell
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","version":"1.0.0"}`

### Verify Frontend
Open browser to: http://localhost:5173
**Expected:** Login page loads

## Demo Tips

### Before Presentation:
1. ✅ Test both patient and doctor views
2. ✅ Ensure at least 2 patients exist
3. ✅ Create some chat history beforehand
4. ✅ Verify one patient has CRITICAL risk

### During Presentation:
1. Show **patient view first** (chatbot demo)
2. Demonstrate **risk assessment** (LOW → CRITICAL)
3. Switch to **doctor view** (monitoring)
4. Highlight **alerts system** for high-risk patients

### Key Features to Highlight:
- 🤖 **AI-powered medical Q&A**
- 🎯 **Real-time risk assessment**
- 👨‍⚕️ **Doctor monitoring dashboard**
- 🚨 **Automatic high-risk alerts**
- 📊 **Risk statistics and trends**

## Ports Summary
- **Backend API:** http://localhost:8000
- **Frontend UI:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

## Quick Commands

### Start Everything (PowerShell)
```powershell
# Terminal 1 - Backend
cd C:\Users\tagor\Documents\GitHub\Med-chatbot
python -m uvicorn backend_api:app --reload --port 8000

# Terminal 2 - Frontend
cd C:\Users\tagor\Documents\GitHub\Med-chatbot\frontend
npm run dev
```

### Stop Everything
```powershell
# Kill backend
Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process

# Frontend: Press Ctrl+C in terminal
```

## File Locations

**Backend Code:** `backend_api.py`  
**Frontend Code:** `frontend/src/`  
**API Docs:** `API_DOCUMENTATION.md`  
**QA Report:** `QA_TEST_REPORT.md`  
**This Guide:** `QUICKSTART.md`

## Support

**Issues?**
1. Check QA_TEST_REPORT.md troubleshooting section
2. Verify backend logs for errors
3. Check browser console for frontend errors
4. Ensure all dependencies installed

---

**Ready to Demo!** 🎉
