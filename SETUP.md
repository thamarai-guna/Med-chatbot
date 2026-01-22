# MedHub - Healthcare Hackathon Project

A simple healthcare app skeleton with patient/doctor roles, authentication, and dashboards.

## Project Structure

```
Med-chatbot/
├── backend/                   # Flask API
│   ├── app.py                # Main Flask app
│   ├── database.py           # SQLite setup
│   ├── models.py             # User model
│   ├── routes/
│   │   ├── auth.py           # Login/Register endpoints
│   │   └── patient.py        # Doctor viewing patients
│   └── requirements.txt
├── frontend/                  # React app
│   ├── src/
│   │   ├── App.js            # Main router
│   │   ├── components/       # React pages
│   │   └── styles/
│   ├── package.json
│   └── .env
└── README.md
```

## Features (Skeleton Only)

✅ **Authentication**
- Register with email, password, and role
- Login with email and password
- Redirect based on role (patient/doctor)

✅ **Patient Dashboard**
- Welcome message
- Empty "Start Today's Check-in" button

✅ **Doctor Dashboard**
- List of all registered patients
- Click patient to view details page

✅ **Backend API**
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/patients` - Get all patients
- `GET /api/patients/<id>` - Get patient details

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm

## Setup & Run

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database.py

# Run Flask server
python app.py
```

Backend will run at: `http://localhost:5000`

### 2. Frontend Setup (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run at: `http://localhost:3000`

## Testing the App

### Create Test Accounts

**Patient Account:**
- Email: `patient@test.com`
- Password: `1234`
- Role: Patient

**Doctor Account:**
- Email: `doctor@test.com`
- Password: `1234`
- Role: Doctor

### Test Flow

1. Go to `http://localhost:3000`
2. Click "Register" → Create patient account
3. Login with patient credentials → See patient dashboard
4. Logout → Register as doctor
5. Login as doctor → See list of patients
6. Click on patient email → View patient details page

## Code Structure Explained

### Backend (Python/Flask)

- **`app.py`**: Flask entry point, initializes CORS and registers route blueprints
- **`database.py`**: SQLite initialization, connection pooling
- **`models.py`**: User model with CRUD operations
- **`routes/auth.py`**: `/login` and `/register` endpoints
- **`routes/patient.py`**: `/patients` and `/patients/<id>` endpoints

### Frontend (React/JavaScript)

- **`App.js`**: Main router, handles authentication state and protected routes
- **`components/Login.js`**: Login form, calls `/api/login`
- **`components/Register.js`**: Registration form, calls `/api/register`
- **`components/PatientDashboard.js`**: Patient welcome page
- **`components/DoctorDashboard.js`**: Doctor's patient list
- **`components/PatientDetail.js`**: Individual patient details
- **`styles/App.css`**: Clean, responsive styling

## Important Notes

⚠️ **Security (Not for Production)**
- Passwords stored as plain text (OK for hackathon demo)
- No JWT tokens (using localStorage for session)
- No input sanitization (for simplicity)
- CORS enabled for all origins

✨ **Next Steps (Future Features)**
- Daily check-in questions
- Symptom logging
- Risk evaluation
- RAG-based medical Q&A
- Doctor notifications
- Patient health metrics

## Troubleshooting

**Port 5000 already in use?**
```bash
python app.py --port 5001
```

**Port 3000 already in use?**
```bash
PORT=3001 npm start
```

**Database issues?**
```bash
# Delete old database and reinitialize
rm backend/medhub.db
python backend/database.py
```

**CORS errors?**
- Make sure backend is running on `:5000`
- Make sure frontend `.env` has `REACT_APP_API_URL=http://localhost:5000/api`

## Contact

Questions? Ask during the hackathon! 🚀

---

**Built for healthcare hackathon - MVP only, not production-ready.**
