# Development Memory - Med-chatbot Healthcare Platform

**Last Updated:** January 22, 2026  
**Project Type:** Healthcare Hackathon (Demo Only - No Production Use)

---

## PROJECT GOAL
Build a centralized hospital web platform integrating:
- AI-based patient monitoring
- Edge-device-based alerting
- Post-discharge AI patient assistance

---

## SYSTEM ARCHITECTURE OVERVIEW

### Distributed System (4 Laptops)
1. **Laptop 1 (Central Server)** - FastAPI Backend + Database
2. **Laptop 2 (Edge Device)** - Vitals Monitoring
3. **Laptop 3 (Edge Device)** - Coma Patient Monitoring
4. **Laptop 4 (Frontend)** - React Web Application + Mobile Access

### Key Constraints
- Only ONE central backend server
- Edge devices communicate ONLY via APIs (no direct communication)
- Multi-user access: Doctors, Nurses, Patients, Admin
- Token-based authentication (JWT)
- Privacy-first: No video streaming
- Dummy/simulated data only

---

## FEATURES OVERVIEW

### ✅ FEATURE 1: Vitals Monitoring (Edge AI)
- **Status:** TODO
- Heart rate, SpO2, Blood pressure monitoring
- Local threshold-based abnormality detection
- API communication with backend

### ✅ FEATURE 2: Coma Patient Monitoring (Edge AI)
- **Status:** TODO
- OpenCV/gyroscope movement detection
- Local processing, alert-only transmission
- Privacy-focused (no video streaming)

### ✅ FEATURE 3: Post-Discharge AI Assistant
- **Status:** TODO
- RAG-based chatbot (brain-related stream)
- Daily symptom check-in
- Adaptive AI-generated questions
- Risk classification (LOW/MEDIUM/HIGH)
- Medical document Q&A

---

## DEVELOPMENT PHASES

### 🔵 PHASE 1: CORE BACKEND & AUTH
**Status:** ✅ COMPLETED (January 22, 2026)

**Completed Items:**
- ✅ Core backend skeleton (FastAPI)
- ✅ Authentication system (JWT)
- ✅ Role-based access control (Doctor/Nurse/Patient/Admin)
- ✅ Database schema (Users, Doctors, Nurses, Patients)
- ✅ API contracts documented
- ✅ All backend routes implemented
- ⏸️ Frontend (React) - PENDING APPROVAL

**Implementation Details:**
- Backend Location: `backend/app/`
- Database Models: User, Doctor, Nurse, Patient
- Routers: auth, doctor, nurse, patient, admin
- JWT-based authentication with role checking
- SQLAlchemy ORM with PostgreSQL
- Auto-generated API docs at `/docs`

**What NOT implemented yet:**
- AI/RAG features
- Vitals processing
- Edge device code
- React frontend

### 🟢 PHASE 2: ALERT INGESTION & DISPLAY
**Status:** ✅ COMPLETED (January 22, 2026)

**Completed Items:**
- ✅ Alerts database table with relationships
- ✅ POST /api/alerts endpoint (edge device ingestion)
- ✅ GET /api/alerts endpoint (role-based retrieval)
- ✅ POST /api/alerts/{id}/acknowledge endpoint
- ✅ Alert schemas and validation
- ✅ Edge device authentication (API key)
- ✅ React Doctor dashboard with alerts
- ✅ React Nurse dashboard with alerts
- ✅ Alert acknowledgement UI
- ✅ Polling-based real-time updates (5-second intervals)
- ✅ Sample edge device simulator script
- ✅ Login page with authentication
- ✅ App.jsx with React Router setup
- ✅ Complete testing documentation (STEP2_TESTING_GUIDE.md)

**Frontend Components Created:**
- Login.jsx - Authentication page
- DoctorDashboard.jsx - Doctor view with alerts panel
- NurseDashboard.jsx - Nurse view with alerts panel
- AlertsPanel.jsx - Reusable alerts display component
- App.jsx - Main routing component
- AuthContext.js - Global auth state
- ProtectedRoute.jsx - Role-based route protection
- api.js - Axios HTTP client

**Backend Components Created:**
- backend/app/models/alert.py - Alert model with enums
- backend/app/schemas/alert.py - Pydantic schemas
- backend/app/routers/alerts.py - Alert endpoints
- edge_devices/send_alert.py - Interactive alert simulator

**Testing Resources:**
- docs/STEP2_TESTING_GUIDE.md - Comprehensive test scenarios

**Implementation Details:**
- Alert Model: alert_id, patient_id, type, severity, source, status
- Severity Levels: LOW, MEDIUM, HIGH
- Alert Types: VITALS_ABNORMAL, COMA_MOVEMENT_DETECTED, HIGH_RISK_FROM_CHATBOT
- Sources: vitals_edge, coma_edge, ai_chatbot
- Status: NEW, ACKNOWLEDGED
- Edge device auth via API_KEY in headers

**What NOT implemented:**
- Actual sensor reading
- OpenCV processing
- AI detection algorithms
- WebSocket (using polling instead)

---

## DECISIONS LOG

### Decision 1: Tech Stack Selection
**Date:** January 22, 2026  
**Decision:**
- **Backend:** FastAPI (Python) - Fast, async, good for APIs
- **Frontend:** React - Component-based, role-based routing
- **Database:** PostgreSQL - Relational data, hospital records
- **Authentication:** JWT tokens - Stateless, scalable
- **Real-time:** WebSocket (future) or Polling - For alerts

**Reasoning:** FastAPI provides excellent performance and auto-documentation. PostgreSQL ensures data integrity for medical records. JWT enables distributed authentication across edge devices.

### Decision 2: Folder Structure (STEP 1)
**Date:** January 22, 2026  
**Decision:**
- Modular backend structure with routers, services, models separation
- Frontend organized by role (doctor/nurse/patient/admin components)
- Edge devices in separate folder (for future steps)
- Centralized docs and dev_memory.md at root

**Reasoning:** Clear separation of concerns. Easy to navigate. Scales well as project grows.

### Decision 3: Database Schema (STEP 1)
**Date:** January 22, 2026  
**Decision:**
- Single `users` table with role field (base for all users)
- Separate tables for `doctors`, `nurses`, `patients` with foreign keys
- Future-ready tables: `alerts`, `vitals`, `chat_history`, `daily_checkins`
- JSONB for flexible data storage in chat/checkin tables

**Reasoning:** Normalized schema. Role-based access control. JSONB allows adaptive questionnaires without schema changes.

### Decision 4: API Endpoint Structure (STEP 1)
**Date:** January 22, 2026  
**Decision:**
- Role-based route prefixes: `/api/doctor`, `/api/nurse`, `/api/patient`, `/api/admin`
- Separate `/api/auth` for authentication
- Future edge device routes: `/api/vitals`, `/api/alert`

**Reasoning:** Clear separation by user role. Easy to implement role-based middleware. RESTful conventions.

### Decision 5: Role-Based Access Implementation
**Date:** January 22, 2026  
**Decision:**
- JWT payload contains user_id and role
- Dependency injection for role checking
- Convenience functions: `get_current_doctor`, `get_current_nurse`, etc.
- 403 Forbidden for unauthorized role access

**Reasoning:** Clean, reusable code. FastAPI dependency system makes it elegant. Clear error messages for debugging.

### Decision 6: Quick Start Scripts
**Date:** January 22, 2026  
**Decision:**
- Created `start_server.bat` (Windows) and `start_server.sh` (Unix)
- Auto-creates venv, installs dependencies, checks .env, starts server
- User-friendly output with URLs

**Reasoning:** Reduces setup friction. Makes it easy for team members to run the project. Good for hackathon demos.

---

## TODO LIST

### Current Sprint (STEP 1) - ✅ BACKEND COMPLETE
- [x] Finalize folder structure
- [x] Design database schema
- [x] Define API endpoint contracts
- [x] Implement authentication system
- [x] Create user models (Doctor, Nurse, Patient, Admin)
- [x] Set up FastAPI project structure
- [ ] Create basic React frontend skeleton (AWAITING APPROVAL)
- [ ] Implement role-based routing (AWAITING APPROVAL)
- [ ] Test authentication flow (AWAITING APPROVAL)

### Future Sprints
- [x] STEP 2: Alert ingestion & display (COMPLETED - January 22, 2026)
- [ ] STEP 3: Vitals edge device + backend integration
- [ ] STEP 4: Coma monitoring edge device
- [ ] STEP 5: RAG chatbot backend
- [ ] STEP 6: Real-time dashboard updates
- [ ] STEP 7: Integration testing

---

## NOTES & ASSUMPTIONS
- Using dummy/simulated data throughout
- Network: All devices on same LAN
- No HIPAA compliance needed (hackathon)
- Focus on architecture demonstration
- Single hospital system (not multi-tenant)

---

## COMPLETED ARTIFACTS (STEP 1)

### Backend Files (18 files)
1. `backend/requirements.txt` - Python dependencies
2. `backend/.env.example` - Environment template
3. `backend/app/config.py` - Settings management
4. `backend/app/database.py` - SQLAlchemy setup
5. `backend/app/main.py` - FastAPI application
6. `backend/app/models/user.py` - User model
7. `backend/app/models/doctor.py` - Doctor model
8. `backend/app/models/nurse.py` - Nurse model
9. `backend/app/models/patient.py` - Patient model
10. `backend/app/schemas/auth.py` - Auth schemas
11. `backend/app/schemas/user.py` - User schemas
12. `backend/app/routers/auth.py` - Auth endpoints
13. `backend/app/routers/doctor.py` - Doctor endpoints
14. `backend/app/routers/nurse.py` - Nurse endpoints
15. `backend/app/routers/patient.py` - Patient endpoints
16. `backend/app/routers/admin.py` - Admin endpoints
17. `backend/app/utils/security.py` - JWT & password hashing
18. `backend/app/utils/dependencies.py` - Role checking

### Documentation Files (5 files)
1. `README.md` - Project overview
2. `dev_memory.md` - This file (development log)
3. `STEP1_SUMMARY.md` - Step 1 completion summary
4. `docs/setup_guide.md` - Installation guide
5. `docs/api_contracts.md` - API documentation

### Helper Scripts (2 files)
1. `backend/start_server.bat` - Windows quick start
2. `backend/start_server.sh` - Unix/Linux/Mac quick start

### Total: 29 files created in STEP 1

---

## STEP 1 COMPLETION CHECKLIST

### Backend Core ✅
- [x] FastAPI application setup
- [x] Database connection and ORM
- [x] Configuration management
- [x] CORS middleware

### Models ✅
- [x] User model (base table)
- [x] Doctor model
- [x] Nurse model
- [x] Patient model
- [x] Enums (UserRole, ShiftType)

### Authentication ✅
- [x] JWT token generation
- [x] Password hashing (bcrypt)
- [x] Token validation
- [x] Role-based access control

### API Endpoints ✅
- [x] POST /api/auth/register
- [x] POST /api/auth/login
- [x] GET /api/auth/me
- [x] GET /api/doctor/patients
- [x] GET /api/doctor/patients/{id}
- [x] GET /api/doctor/alerts (placeholder)
- [x] GET /api/nurse/patients
- [x] GET /api/nurse/alerts (placeholder)
- [x] GET /api/patient/profile
- [x] GET /api/patient/chat (placeholder)
- [x] POST /api/patient/chat (placeholder)
- [x] POST /api/admin/users
- [x] GET /api/admin/users
- [x] POST /api/admin/patients
- [x] POST /api/admin/doctors/{user_id}
- [x] POST /api/admin/nurses/{user_id}

### Documentation ✅
- [x] README.md - Project overview
- [x] dev_memory.md - Development log
- [x] STEP1_SUMMARY.md - Completion summary
- [x] docs/setup_guide.md - Installation guide
- [x] docs/api_contracts.md - API reference
- [x] docs/database_setup.md - Database guide
- [x] docs/architecture.md - System architecture
- [x] docs/testing_guide.md - Testing procedures

### Helper Tools ✅
- [x] start_server.bat - Windows launcher
- [x] start_server.sh - Unix launcher
- [x] requirements.txt - Dependencies
- [x] .env.example - Environment template

---

## WHAT'S NEXT?

### Option 1: Frontend Development
Build React web application with role-based dashboards.

### Option 2: Edge Device - Vitals Monitor (STEP 2)
Build Python service to read/simulate vitals and detect abnormalities.

### Option 3: Edge Device - Coma Monitor (STEP 3)
Build OpenCV-based movement detection system.

### Recommended: Frontend First
This will allow testing the complete flow before adding edge devices.

---
