# Med-Chatbot - Centralized Hospital Platform

**Healthcare Hackathon Project**  
A distributed hospital web platform integrating AI-based patient monitoring, edge device alerting, and post-discharge patient assistance.

---

## 🚀 Project Status

**Current Phase:** ✅ STEP 1 COMPLETE - Backend Core & Authentication  
**Next Phase:** STEP 2 - Vitals Monitoring Edge Device

---

## 📋 System Overview

### Architecture
- **Laptop 1 (Central Server):** FastAPI Backend + PostgreSQL Database
- **Laptop 2 (Edge Device):** Vitals Monitoring (Heart Rate, SpO2, BP) - *Coming in STEP 2*
- **Laptop 3 (Edge Device):** Coma Patient Monitoring (OpenCV) - *Coming in STEP 3*
- **Laptop 4 (Frontend):** React Web Application - *Coming Next*

### Core Features
1. **Vitals Monitoring** - Edge AI-based threshold detection
2. **Coma Patient Monitoring** - Movement detection via camera/gyro
3. **Post-Discharge AI Assistant** - RAG-based chatbot with symptom tracking

---

## 🎯 STEP 1 Deliverables (COMPLETED)

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
├── docs/
│   ├── setup_guide.md   # Installation instructions
│   └── api_contracts.md # API documentation
├── dev_memory.md        # Development decisions log
└── README.md
```

### 🔌 API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and receive JWT
- `GET /api/auth/me` - Get current user info

#### Doctor Routes
- `GET /api/doctor/patients` - Get assigned patients
- `GET /api/doctor/patients/{id}` - Get patient details
- `GET /api/doctor/alerts` - Get alerts (placeholder)

#### Nurse Routes
- `GET /api/nurse/patients` - Get ward patients
- `GET /api/nurse/alerts` - Get alerts (placeholder)

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

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 13+

### Quick Start

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
# Edit .env with your database credentials

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 📚 Documentation

- **[Setup Guide](docs/setup_guide.md)** - Detailed installation steps
- **[API Contracts](docs/api_contracts.md)** - Complete API documentation
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

### Future Tables (STEP 2+)
- Alerts (vitals, coma movement)
- Vitals (time-series data)
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
