# System Architecture - Med-Chatbot Hospital Platform

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MED-CHATBOT PLATFORM                          │
│                  Distributed Hospital System                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   LAPTOP 2       │         │   LAPTOP 3       │
│  Edge Device     │         │  Edge Device     │
│                  │         │                  │
│  Vitals Monitor  │         │  Coma Monitor    │
│  - Heart Rate    │         │  - OpenCV        │
│  - SpO2          │         │  - Movement      │
│  - Blood Pressure│         │  - Gyroscope     │
│                  │         │                  │
│  [Python Service]│         │  [Python Service]│
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ POST /api/vitals          │ POST /api/alert
         │ POST /api/alert           │
         │                            │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │      LAPTOP 1 (Central Server) │
         │                                 │
         │   ┌─────────────────────────┐  │
         │   │   FastAPI Backend       │  │
         │   │   (Port 8000)           │  │
         │   │                         │  │
         │   │  /api/auth              │  │
         │   │  /api/doctor            │  │
         │   │  /api/nurse             │  │
         │   │  /api/patient           │  │
         │   │  /api/admin             │  │
         │   │  /api/vitals  (future)  │  │
         │   │  /api/alert   (future)  │  │
         │   └──────────┬──────────────┘  │
         │              │                  │
         │   ┌──────────▼──────────────┐  │
         │   │   PostgreSQL Database   │  │
         │   │   (Port 5432)           │  │
         │   │                         │  │
         │   │  - users                │  │
         │   │  - doctors              │  │
         │   │  - nurses               │  │
         │   │  - patients             │  │
         │   │  - alerts (future)      │  │
         │   │  - vitals (future)      │  │
         │   └─────────────────────────┘  │
         └────────────────────────────────┘
                      │
                      │ HTTP REST API
                      │ JWT Authentication
                      │
         ┌────────────▼────────────┐
         │    LAPTOP 4 + Phones    │
         │   React Frontend        │
         │   (Port 3000)           │
         │                         │
         │  - Login Page           │
         │  - Doctor Dashboard     │
         │  - Nurse Dashboard      │
         │  - Patient Portal       │
         │  - Admin Panel          │
         └─────────────────────────┘
```

---

## Authentication Flow

```
┌─────────┐                 ┌─────────┐                 ┌──────────┐
│  User   │                 │ Backend │                 │ Database │
│ Browser │                 │   API   │                 │          │
└────┬────┘                 └────┬────┘                 └────┬─────┘
     │                           │                           │
     │  POST /api/auth/login    │                           │
     │  {email, password}       │                           │
     ├─────────────────────────>│                           │
     │                           │  Check credentials        │
     │                           ├──────────────────────────>│
     │                           │                           │
     │                           │  User data                │
     │                           │<──────────────────────────┤
     │                           │                           │
     │                           │  Generate JWT token       │
     │                           │  (contains user_id, role) │
     │                           │                           │
     │  {access_token, user}    │                           │
     │<─────────────────────────┤                           │
     │                           │                           │
     │  Store token in memory   │                           │
     │  or localStorage         │                           │
     │                           │                           │
     │  GET /api/doctor/patients │                          │
     │  Header: Bearer <token>  │                           │
     ├─────────────────────────>│                           │
     │                           │  Verify & decode token    │
     │                           │  Check role = doctor      │
     │                           │                           │
     │                           │  Query assigned patients  │
     │                           ├──────────────────────────>│
     │                           │                           │
     │                           │  Patient list             │
     │                           │<──────────────────────────┤
     │                           │                           │
     │  Patient data            │                           │
     │<─────────────────────────┤                           │
     │                           │                           │
```

---

## Database Schema (ER Diagram)

```
┌─────────────────────┐
│       USERS         │
│ (Base for all)      │
├─────────────────────┤
│ id (PK)             │
│ email (UNIQUE)      │
│ password_hash       │
│ role (ENUM)         │──┐
│ full_name           │  │
│ phone               │  │
│ is_active           │  │
│ created_at          │  │
│ updated_at          │  │
└─────────────────────┘  │
           │              │
           │1             │1
    ┌──────┴──────┬───────┴────┬──────────────┐
    │             │            │              │
    │1            │1           │1             │1
┌───▼────────┐ ┌──▼────────┐ ┌▼───────────┐ ┌▼──────┐
│  DOCTORS   │ │  NURSES   │ │  PATIENTS  │ │ ADMIN │
├────────────┤ ├───────────┤ ├────────────┤ └───────┘
│ id (PK)    │ │ id (PK)   │ │ id (PK)    │
│ user_id FK │ │ user_id FK│ │ user_id FK │
│ specializ. │ │ ward_assgn│ │ patient_no │
│ license_no │ │ shift     │ │ dob        │
│ department │ └───────────┘ │ gender     │
└─────┬──────┘               │ admission  │
      │                      │ discharge  │
      │                      │ doctor_id  │◄────┐
      │                      │ ward       │     │
      │                      │ bed_number │     │
      │                      │ discharged │     │
      │                      └────────────┘     │
      │                                         │
      └─────────────────────────────────────────┘
                       N:1
              (assigned patients)

Future Tables (STEP 2+):

┌────────────────┐      ┌──────────────┐
│    ALERTS      │      │   VITALS     │
├────────────────┤      ├──────────────┤
│ id (PK)        │      │ id (PK)      │
│ patient_id FK  │      │ patient_id FK│
│ alert_type     │      │ heart_rate   │
│ severity       │      │ spo2         │
│ message        │      │ bp_systolic  │
│ acknowledged   │      │ bp_diastolic │
│ acknowledged_by│      │ temperature  │
│ created_at     │      │ recorded_at  │
└────────────────┘      └──────────────┘

┌───────────────────┐   ┌──────────────────┐
│  CHAT_HISTORY     │   │ DAILY_CHECKINS   │
├───────────────────┤   ├──────────────────┤
│ id (PK)           │   │ id (PK)          │
│ patient_id FK     │   │ patient_id FK    │
│ message           │   │ questions (JSONB)│
│ is_bot            │   │ answers (JSONB)  │
│ risk_level        │   │ risk_classify    │
│ created_at        │   │ created_at       │
└───────────────────┘   └──────────────────┘
```

---

## API Request Flow

```
┌──────────────────────────────────────────────────────────┐
│                  API Request Lifecycle                    │
└──────────────────────────────────────────────────────────┘

1. Request Arrives
   ↓
2. CORS Middleware (allow origins)
   ↓
3. Route Matching (/api/doctor/patients)
   ↓
4. Dependency Injection
   ├─ Extract JWT from Authorization header
   ├─ Decode and validate token
   ├─ Query user from database
   └─ Check user role matches required role
   ↓
5. Route Handler (doctor.py)
   ├─ Get doctor record
   ├─ Query assigned patients
   └─ Format response
   ↓
6. Response Serialization (Pydantic schema)
   ↓
7. Return JSON response
```

---

## Directory Structure (Detailed)

```
Med-chatbot/
├── backend/                    # Central Server Backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py        # User, UserRole enum
│   │   │   ├── doctor.py      # Doctor model
│   │   │   ├── nurse.py       # Nurse, ShiftType enum
│   │   │   └── patient.py     # Patient model
│   │   │
│   │   ├── schemas/           # Pydantic request/response
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Login, Register, Token
│   │   │   └── user.py        # Patient/Doctor/Nurse DTOs
│   │   │
│   │   ├── routers/           # API endpoint handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # /api/auth/*
│   │   │   ├── doctor.py      # /api/doctor/*
│   │   │   ├── nurse.py       # /api/nurse/*
│   │   │   ├── patient.py     # /api/patient/*
│   │   │   └── admin.py       # /api/admin/*
│   │   │
│   │   ├── utils/             # Helper functions
│   │   │   ├── __init__.py
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   └── dependencies.py # Role checking
│   │   │
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app entry
│   │   ├── config.py         # Settings (Pydantic)
│   │   └── database.py       # SQLAlchemy setup
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment template
│   ├── start_server.bat      # Windows launcher
│   └── start_server.sh       # Unix launcher
│
├── frontend/                  # React Web App (FUTURE)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
│
├── edge_devices/              # Edge Device Code (FUTURE)
│   ├── vitals_monitor/        # Laptop 2
│   │   ├── main.py
│   │   ├── vitals_reader.py
│   │   └── threshold_detector.py
│   │
│   └── coma_monitor/          # Laptop 3
│       ├── main.py
│       ├── camera_processor.py
│       └── movement_detector.py
│
├── docs/                      # Documentation
│   ├── setup_guide.md
│   ├── api_contracts.md
│   └── database_setup.md
│
├── dev_memory.md             # Development log
├── STEP1_SUMMARY.md          # Step 1 completion
└── README.md                 # Project overview
```

---

## Technology Stack

```
┌─────────────────────────────────────────┐
│           TECHNOLOGY STACK              │
└─────────────────────────────────────────┘

Backend (Laptop 1 - Central Server)
├── FastAPI 0.109.0          # Web framework
├── Uvicorn                  # ASGI server
├── SQLAlchemy 2.0.25        # ORM
├── PostgreSQL 13+           # Database
├── Pydantic                 # Data validation
├── python-jose              # JWT handling
├── passlib + bcrypt         # Password hashing
└── python-multipart         # File uploads

Frontend (Laptop 4 + Phones) - FUTURE
├── React 18                 # UI framework
├── React Router             # Routing
├── Axios                    # HTTP client
├── Context API              # State management
└── TailwindCSS / Material-UI # Styling

Edge Devices (Laptop 2 & 3) - FUTURE
├── Python 3.9+              # Base language
├── OpenCV                   # Video processing
├── NumPy                    # Numerical operations
├── Requests                 # HTTP client
└── Schedule                 # Task scheduling

AI/RAG (STEP 4) - FUTURE
├── LangChain                # RAG framework
├── OpenAI API / Llama       # LLM
├── ChromaDB / FAISS         # Vector database
└── Sentence Transformers    # Embeddings
```

---

## Data Flow: Vitals Monitoring (Future - STEP 2)

```
┌──────────────────────────────────────────────────────────┐
│              Vitals Monitoring Flow                       │
└──────────────────────────────────────────────────────────┘

Laptop 2 (Edge Device)
  │
  ├─ Read Sensor Data
  │  ├─ Heart Rate: 75 bpm
  │  ├─ SpO2: 98%
  │  └─ BP: 120/80 mmHg
  │
  ├─ Local Threshold Check
  │  └─ Heart Rate > 100? → ALERT!
  │
  ├─ POST /api/vitals
  │  {
  │    patient_id: 1,
  │    heart_rate: 105,
  │    spo2: 98,
  │    bp: "120/80"
  │  }
  │
  └─ POST /api/alert (if abnormal)
     {
       patient_id: 1,
       alert_type: "vitals",
       severity: "medium",
       message: "Heart rate elevated: 105 bpm"
     }
     │
     ▼
Laptop 1 (Central Server)
  │
  ├─ Store vitals in database
  ├─ Store alert in database
  ├─ Identify assigned doctor
  └─ Mark alert as "unacknowledged"
     │
     ▼
Laptop 4 / Phones (Frontend)
  │
  ├─ Poll /api/doctor/alerts
  ├─ Display red notification
  ├─ Show patient details
  └─ Doctor clicks "Acknowledge"
     │
     ▼
Backend
  │
  └─ PUT /api/doctor/alerts/1/ack
     └─ Update alert.is_acknowledged = True
```

---

## Security Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Security Layers                          │
└──────────────────────────────────────────────────────────┘

Layer 1: Password Security
  ├─ bcrypt hashing (cost factor 12)
  ├─ Salt per password (automatic)
  └─ Never store plaintext

Layer 2: JWT Authentication
  ├─ HS256 algorithm
  ├─ 30-minute expiration
  ├─ Payload: {sub: user_id, role: "doctor"}
  └─ Secret key from environment

Layer 3: Role-Based Access Control
  ├─ Middleware checks role
  ├─ 403 if wrong role
  └─ User can only see their data

Layer 4: Database
  ├─ Parameterized queries (SQL injection protection)
  ├─ Foreign key constraints
  └─ Cascading deletes

Layer 5: Network (Future)
  ├─ HTTPS only
  ├─ CORS configured
  └─ Rate limiting

Not Implemented (Hackathon):
  ├─ Email verification
  ├─ 2FA
  ├─ Password reset
  ├─ Session management
  └─ Audit logging
```

---

This architecture document will be updated as we progress through STEP 2, 3, 4, etc.
