# Med-Chatbot Backend Setup Guide

## Prerequisites
- Python 3.9+
- PostgreSQL 13+

## Installation Steps

### 1. Install PostgreSQL
Download and install PostgreSQL from https://www.postgresql.org/download/

### 2. Create Database
```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE med_chatbot;

# Exit
\q
```

### 3. Setup Python Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and update:
# - DATABASE_URL with your PostgreSQL credentials
# - SECRET_KEY with a secure random string
```

### 5. Run the Application
```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the API

### 1. Create Admin User
```bash
POST http://localhost:8000/api/auth/register
{
  "email": "admin@hospital.com",
  "password": "admin123",
  "full_name": "System Admin",
  "role": "admin"
}
```

### 2. Login
```bash
POST http://localhost:8000/api/auth/login
{
  "email": "admin@hospital.com",
  "password": "admin123"
}
```

### 3. Use the Token
Copy the `access_token` from login response and add to headers:
```
Authorization: Bearer <your_token_here>
```

## Database Schema
The database tables are created automatically on first run:
- users
- doctors
- nurses
- patients

Future tables (will be added in later steps):
- alerts
- vitals
- chat_history
- daily_checkins

## Next Steps (STEP 2+)
- Edge device integration
- Vitals monitoring
- Alert system
- RAG chatbot
