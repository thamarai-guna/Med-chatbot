# Med-Chatbot - Centralized Hospital Platform

**Healthcare Hackathon Project**  
A distributed hospital web platform integrating AI-based patient monitoring, edge device alerting, and post-discharge patient assistance.

---

## 🚀 Project Status

**Current Phase:** ✅ STEP 2 COMPLETE - Alert Ingestion & Display  
**Next Phase:** STEP 3 - TBD

---

## 📋 System Overview

### Architecture
- **Laptop 1 (Central Server):** FastAPI Backend + PostgreSQL Database
- **Laptop 2 (Edge Device):** Vitals Monitoring (Heart Rate, SpO2, BP) - *Simulated*
- **Laptop 3 (Edge Device):** Coma Patient Monitoring (OpenCV) - *Simulated*
- **Laptop 4 (Frontend):** React Web Application - ✅ Implemented

### Core Features
1. **✅ Alert System** - Edge device alert ingestion and display
2. **Vitals Monitoring** - Edge AI-based threshold detection (*Coming*)
3. **Coma Patient Monitoring** - Movement detection via camera/gyro (*Coming*)
4. **Post-Discharge AI Assistant** - RAG-based chatbot with symptom tracking (*Coming*)

---

## 🎯 STEP 1 Deliverables (COMPLETED)

**Status:** ✅ Backend Core & Authentication

### ✅ Backend Implementation
- **Tech Stack:** FastAPI + SQLAlchemy + PostgreSQL
- **Authentication:** JWT token-based with role checking
- **Role-Based Access:** Doctor, Nurse, Patient, Admin
- **Database Schema:** Users, Doctors, Nurses, Patients
- **API Endpoints:** 16 endpoints across 5 routers

### 📂 Folder Structure
```
Med-chatbot/
├── backend/              # Central Server (FastAPI)
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── routers/     # API endpoints
│   │   ├── utils/       # Security & dependencies
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/            # React Web Application
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── context/     # Auth context
│   │   ├── pages/       # Dashboard pages
│   │   ├── services/    # API client
│   │   ├── utils/       # Route protection
│   │   └── App.jsx
│   └── package.json
├── edge_devices/        # Edge device simulators
│   └── send_alert.py    # Alert simulator script
├── docs/
│   ├── setup_guide.md   # Installation instructions
│   ├── api_contracts.md # API documentation
│   ├── STEP2_TESTING_GUIDE.md  # Testing instructions
│   └── STEP2_SUMMARY.md # STEP 2 completion report
├── dev_memory.md        # Development decisions log
└── README.md
```

### 🔌 API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and receive JWT
- `GET /api/auth/me` - Get current user info

#### Alert System (NEW in STEP 2)
- `POST /api/alerts` - Edge device alert ingestion (API Key auth)
- `GET /api/alerts` - Get user's alerts with role-based filtering
- `POST /api/alerts/{id}/acknowledge` - Acknowledge an alert

#### Doctor Routes
- `GET /api/doctor/patients` - Get assigned patients
- `GET /api/doctor/patients/{id}` - Get patient details

#### Nurse Routes
- `GET /api/nurse/patients` - Get ward patients

#### Patient Routes
- `GET /api/patient/profile` - Get own profile
- `GET /api/patient/chat` - Get chat history (placeholder)
- `POST /api/patient/chat` - Send message (placeholder)

#### Admin Routes
- `POST /api/admin/users` - Create user
- `GET /api/admin/users` - List all users
- `POST /api/admin/patients` - Register patient
- `POST /api/admin/doctors/{user_id}` - Create doctor profile
- `POST /api/admin/nurses/{user_id}` - Create nurse profile

---

## 🎯 STEP 2 Deliverables (COMPLETED)

**Status:** ✅ Alert Ingestion & Display

### Backend Features
- **Alert Model:** Database table with enums (AlertType, AlertSeverity, AlertSource, AlertStatus)
- **Alert API:** 3 endpoints for create, retrieve, acknowledge
- **Edge Device Auth:** API key authentication via X-API-Key header
- **Role-Based Filtering:** Doctors see assigned patients, nurses see ward patients

### Frontend Features
- **Login Page:** Authentication with role-based navigation
- **Doctor Dashboard:** Alerts panel + patient list with tabs
- **Nurse Dashboard:** Alerts panel + ward patient list with tabs
- **AlertsPanel Component:** Real-time polling (5 sec), filtering, acknowledge functionality
- **Severity Styling:** Color-coded alerts (red/yellow/green)
- **Protected Routes:** Role-based access control

### Edge Device Tools
- **send_alert.py:** Interactive alert simulator with 5 options
- Supports all alert types (Vitals, Coma, Chatbot)
- Health check on startup

### Documentation
- **STEP2_TESTING_GUIDE.md:** 10+ test scenarios with validation steps
- **STEP2_SUMMARY.md:** Complete technical documentation

**Files Created:** 26 new files, 5 modified files

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# 1. Install PostgreSQL and create database
psql -U postgres
CREATE DATABASE med_chatbot;
\q

# 2. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials and API key

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start development server
npm start
```

### Edge Device Simulator

```bash
# Run alert simulator
cd edge_devices
python send_alert.py
```

### Access Applications
- **Backend API:** http://localhost:8000/docs
- **Frontend App:** http://localhost:3000
- **Health Check:** http://localhost:8000/health

---

## 📚 Documentation

- **[Setup Guide](docs/setup_guide.md)** - Detailed installation steps
- **[API Contracts](docs/api_contracts.md)** - Complete API documentation
- **[STEP 2 Testing Guide](docs/STEP2_TESTING_GUIDE.md)** - Test scenarios and validation
- **[STEP 2 Summary](docs/STEP2_SUMMARY.md)** - Technical implementation details
- **[Dev Memory](dev_memory.md)** - Project decisions and progress log

---

## 🔐 Database Schema

### Users Table
Base table for all user roles with email, password, role, and profile info.

### Doctors Table
Specialization, license number, department. Links to Users table.

### Nurses Table
Ward assignment, shift info. Links to Users table.

### Patients Table
Patient number, DOB, admission/discharge dates, assigned doctor, ward, bed number.

### Alerts Table (NEW in STEP 2)
Alert type, message, severity, source, status, acknowledged_by, timestamps. Links to Patients and Users.
- Chat History (AI assistant)
- Daily Check-ins (symptom tracking)

---

## 🧪 Testing

### Create Admin User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hospital.com",
    "password": "admin123",
    "full_name": "System Admin",
    "role": "admin"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hospital.com",
    "password": "admin123"
  }'
```

Use the returned `access_token` in subsequent requests:
```
Authorization: Bearer <your_token>
```

---

## 📅 Development Roadmap

- [x] **STEP 1:** Core backend, authentication, role-based access
- [ ] **STEP 2:** Vitals monitoring edge device + backend integration
- [ ] **STEP 3:** Coma monitoring edge device
- [ ] **STEP 4:** RAG chatbot backend
- [ ] **STEP 5:** Alert aggregation system
- [ ] **STEP 6:** React frontend with role-based dashboards
- [ ] **STEP 7:** Real-time updates (WebSocket)
- [ ] **STEP 8:** Integration testing

---

## 🎓 Key Design Decisions

### Why FastAPI?
- Fast, async support
- Auto-generated API docs
- Strong typing with Pydantic
- Perfect for microservice communication

### Why JWT?
- Stateless authentication
- Works across distributed edge devices
- Easy to validate on each service

### Why PostgreSQL?
- ACID compliance for medical records
- Relational integrity
- JSONB for flexible data (chat, questionnaires)

### Why Separate Edge Devices?
- Privacy: Process video/vitals locally
- Efficiency: Only send alerts, not raw data
- Scalability: Add more edge devices easily
- Realistic hospital architecture

---

## ⚠️ Important Notes

- **Not for Production:** This is a hackathon demo
- **Dummy Data Only:** No real patient information
- **Security:** Change SECRET_KEY in production
- **Network:** All devices must be on same LAN
- **Database:** Backup before schema changes

---

## 📞 Next Steps

**Awaiting confirmation to proceed with:**
1. React frontend skeleton
2. Role-based dashboard routing
3. Login page and authentication flow

Once approved, we'll move to **STEP 2: Vitals Monitoring Edge Device**.

---

## 📄 License

Hackathon Project - Educational Use Only
