# Testing Guide - STEP 1

Complete testing procedures for the backend API.

---

## Prerequisites

1. Backend server running: `uvicorn app.main:app --reload`
2. PostgreSQL database created and connected
3. API documentation accessible at http://localhost:8000/docs

---

## Testing Tools

### Option 1: Swagger UI (Recommended for beginners)
- Visit http://localhost:8000/docs
- Interactive interface with "Try it out" buttons
- Automatic request formatting

### Option 2: cURL (Command line)
- Copy-paste commands from this guide
- Works in any terminal

### Option 3: Postman / Insomnia
- Import the API endpoints
- Save tokens for reuse

---

## Test Sequence

### 1️⃣ Health Check

**Endpoint:** `GET /health`

**cURL:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

### 2️⃣ Register Admin User

**Endpoint:** `POST /api/auth/register`

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hospital.com",
    "password": "admin123",
    "full_name": "System Admin",
    "role": "admin",
    "phone": "1234567890"
  }'
```

**Expected Response (201):**
```json
{
  "id": 1,
  "email": "admin@hospital.com",
  "role": "admin",
  "full_name": "System Admin",
  "phone": "1234567890",
  "is_active": true,
  "created_at": "2026-01-22T10:00:00Z"
}
```

---

### 3️⃣ Register Doctor User

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "doctor123",
    "full_name": "Dr. John Smith",
    "role": "doctor",
    "phone": "9876543210"
  }'
```

---

### 4️⃣ Register Nurse User

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nurse@hospital.com",
    "password": "nurse123",
    "full_name": "Nurse Jane Doe",
    "role": "nurse",
    "phone": "5555555555"
  }'
```

---

### 5️⃣ Register Patient User

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@hospital.com",
    "password": "patient123",
    "full_name": "John Patient",
    "role": "patient",
    "phone": "1111111111"
  }'
```

---

### 6️⃣ Login as Doctor

**Endpoint:** `POST /api/auth/login`

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "doctor123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "doctor@hospital.com",
    "role": "doctor",
    "full_name": "Dr. John Smith"
  }
}
```

**⚠️ IMPORTANT:** Copy the `access_token` for use in subsequent requests!

---

### 7️⃣ Create Doctor Profile (as Admin)

First, login as admin and get token.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/admin/doctors/2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE" \
  -d '{
    "specialization": "Cardiology",
    "license_number": "MD12345",
    "department": "Emergency"
  }'
```

---

### 8️⃣ Create Nurse Profile (as Admin)

**cURL:**
```bash
curl -X POST http://localhost:8000/api/admin/nurses/3 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE" \
  -d '{
    "ward_assigned": "ICU",
    "shift": "morning"
  }'
```

---

### 9️⃣ Register Complete Patient (as Admin)

**Endpoint:** `POST /api/admin/patients`

**cURL:**
```bash
curl -X POST http://localhost:8000/api/admin/patients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE" \
  -d '{
    "email": "patient2@hospital.com",
    "password": "patient123",
    "full_name": "Jane Patient",
    "phone": "2222222222",
    "patient_number": "P001",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "assigned_doctor_id": 1,
    "medical_history": "No known allergies",
    "ward": "ICU",
    "bed_number": "A-101"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "patient_number": "P001",
  "full_name": "Jane Patient",
  "email": "patient2@hospital.com",
  "date_of_birth": "1990-05-15",
  "gender": "female",
  "admission_date": "2026-01-22T10:30:00Z",
  "discharge_date": null,
  "assigned_doctor_id": 1,
  "is_discharged": false,
  "ward": "ICU",
  "bed_number": "A-101"
}
```

---

### 🔟 Get Current User Info

**Endpoint:** `GET /api/auth/me`

**cURL:**
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_DOCTOR_TOKEN_HERE"
```

---

### 1️⃣1️⃣ Get Assigned Patients (as Doctor)

**Endpoint:** `GET /api/doctor/patients`

**cURL:**
```bash
curl http://localhost:8000/api/doctor/patients \
  -H "Authorization: Bearer YOUR_DOCTOR_TOKEN_HERE"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "patient_number": "P001",
    "full_name": "Jane Patient",
    "email": "patient2@hospital.com",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "admission_date": "2026-01-22T10:30:00Z",
    "discharge_date": null,
    "assigned_doctor_id": 1,
    "is_discharged": false,
    "ward": "ICU",
    "bed_number": "A-101"
  }
]
```

---

### 1️⃣2️⃣ Get Specific Patient (as Doctor)

**Endpoint:** `GET /api/doctor/patients/{patient_id}`

**cURL:**
```bash
curl http://localhost:8000/api/doctor/patients/1 \
  -H "Authorization: Bearer YOUR_DOCTOR_TOKEN_HERE"
```

---

### 1️⃣3️⃣ Get Ward Patients (as Nurse)

First, login as nurse to get token.

**Endpoint:** `GET /api/nurse/patients`

**cURL:**
```bash
curl http://localhost:8000/api/nurse/patients \
  -H "Authorization: Bearer YOUR_NURSE_TOKEN_HERE"
```

---

### 1️⃣4️⃣ Get Patient Profile (as Patient)

First, login as patient to get token.

**Endpoint:** `GET /api/patient/profile`

**cURL:**
```bash
curl http://localhost:8000/api/patient/profile \
  -H "Authorization: Bearer YOUR_PATIENT_TOKEN_HERE"
```

---

### 1️⃣5️⃣ List All Users (as Admin)

**Endpoint:** `GET /api/admin/users`

**cURL:**
```bash
curl http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN_HERE"
```

---

## Error Testing

### Test 1: Invalid Credentials

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@hospital.com",
    "password": "wrongpass"
  }'
```

**Expected (401):**
```json
{
  "detail": "Incorrect email or password"
}
```

---

### Test 2: Duplicate Email

Register a user with the same email twice.

**Expected (400):**
```json
{
  "detail": "Email already registered"
}
```

---

### Test 3: Access Without Token

**cURL:**
```bash
curl http://localhost:8000/api/doctor/patients
```

**Expected (403):**
```json
{
  "detail": "Not authenticated"
}
```

---

### Test 4: Wrong Role Access

Try to access doctor endpoints with a nurse token.

**cURL:**
```bash
curl http://localhost:8000/api/doctor/patients \
  -H "Authorization: Bearer YOUR_NURSE_TOKEN_HERE"
```

**Expected (403):**
```json
{
  "detail": "Access forbidden. Required roles: ['doctor']"
}
```

---

### Test 5: Invalid Token

**cURL:**
```bash
curl http://localhost:8000/api/doctor/patients \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

---

## Automated Testing Script (Python)

Save as `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_register_and_login():
    print("Testing registration and login...")
    
    # Register
    register_data = {
        "email": "test@hospital.com",
        "password": "test123",
        "full_name": "Test User",
        "role": "doctor"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"Register Status: {response.status_code}")
    
    # Login
    login_data = {
        "email": "test@hospital.com",
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Token received: {token[:20]}...")
        return token
    
    return None

def test_protected_endpoint(token):
    print("\nTesting protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    test_health()
    token = test_register_and_login()
    if token:
        test_protected_endpoint(token)
```

**Run:**
```bash
pip install requests
python test_api.py
```

---

## Swagger UI Testing (Easiest Method)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/auth/register`
3. Click "Try it out"
4. Fill in the form
5. Click "Execute"
6. See the response

For protected endpoints:
1. First, register and login to get a token
2. Click the "Authorize" button at the top
3. Paste your token: `Bearer <your_token>`
4. Click "Authorize"
5. Now all requests will include the token

---

## Test Checklist

- [ ] ✅ Server starts without errors
- [ ] ✅ Health endpoint returns 200
- [ ] ✅ Can register admin user
- [ ] ✅ Can register doctor user
- [ ] ✅ Can register nurse user
- [ ] ✅ Can register patient user
- [ ] ✅ Can login with correct credentials
- [ ] ✅ Cannot login with wrong credentials
- [ ] ✅ Cannot register duplicate email
- [ ] ✅ Token received after login
- [ ] ✅ Can access protected endpoint with token
- [ ] ✅ Cannot access protected endpoint without token
- [ ] ✅ Doctor can create profile
- [ ] ✅ Nurse can create profile
- [ ] ✅ Admin can register patients
- [ ] ✅ Doctor can see assigned patients
- [ ] ✅ Nurse can see ward patients
- [ ] ✅ Patient can see own profile
- [ ] ✅ Admin can list all users
- [ ] ✅ Wrong role gets 403 Forbidden
- [ ] ✅ Invalid token gets 401 Unauthorized

---

## Database Verification

After testing, verify data in database:

```sql
psql -U postgres -d med_chatbot

-- Count users
SELECT COUNT(*), role FROM users GROUP BY role;

-- List doctors
SELECT u.full_name, d.specialization 
FROM users u 
JOIN doctors d ON u.id = d.user_id;

-- List patients
SELECT u.full_name, p.patient_number, p.ward, p.bed_number
FROM users u
JOIN patients p ON u.id = p.user_id;
```

---

All tests passing = ✅ STEP 1 Complete!
