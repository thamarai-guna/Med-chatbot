# API Contracts - Med-Chatbot Hospital Platform

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints except `/auth/register` and `/auth/login` require JWT authentication.

**Header Format:**
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### 1. Register User
**POST** `/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "role": "doctor",  // doctor | nurse | patient | admin
  "phone": "1234567890"  // optional
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "doctor",
  "full_name": "John Doe",
  "phone": "1234567890",
  "is_active": true,
  "created_at": "2026-01-22T10:00:00Z"
}
```

---

### 2. Login
**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "doctor@hospital.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "doctor@hospital.com",
    "role": "doctor",
    "full_name": "Dr. John Smith"
  }
}
```

---

### 3. Get Current User
**GET** `/auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "doctor@hospital.com",
  "role": "doctor",
  "full_name": "Dr. John Smith",
  "phone": "1234567890",
  "is_active": true,
  "created_at": "2026-01-22T10:00:00Z"
}
```

---

## Doctor Endpoints

### 4. Get Assigned Patients
**GET** `/doctor/patients`

**Headers:** `Authorization: Bearer <doctor_token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "patient_number": "P001",
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "admission_date": "2026-01-20T08:00:00Z",
    "discharge_date": null,
    "assigned_doctor_id": 1,
    "is_discharged": false,
    "ward": "ICU",
    "bed_number": "A-101"
  }
]
```

---

### 5. Get Patient Details
**GET** `/doctor/patients/{patient_id}`

**Headers:** `Authorization: Bearer <doctor_token>`

**Response (200):** Same as patient object above

---

### 6. Get Alerts (Placeholder)
**GET** `/doctor/alerts`

**Headers:** `Authorization: Bearer <doctor_token>`

**Response (200):**
```json
{
  "message": "Alert functionality will be implemented in STEP 2",
  "alerts": []
}
```

---

## Nurse Endpoints

### 7. Get Ward Patients
**GET** `/nurse/patients`

**Headers:** `Authorization: Bearer <nurse_token>`

**Response (200):** Array of patient objects (same structure as doctor endpoint)

---

### 8. Get Alerts (Placeholder)
**GET** `/nurse/alerts`

**Headers:** `Authorization: Bearer <nurse_token>`

**Response (200):**
```json
{
  "message": "Alert functionality will be implemented in STEP 2",
  "alerts": []
}
```

---

## Patient Endpoints

### 9. Get Patient Profile
**GET** `/patient/profile`

**Headers:** `Authorization: Bearer <patient_token>`

**Response (200):** Patient object

---

### 10. Get Chat History (Placeholder)
**GET** `/patient/chat`

**Headers:** `Authorization: Bearer <patient_token>`

**Response (200):**
```json
{
  "message": "Chat functionality will be implemented in STEP 4",
  "chat_history": []
}
```

---

### 11. Send Chat Message (Placeholder)
**POST** `/patient/chat`

**Headers:** `Authorization: Bearer <patient_token>`

**Response (200):**
```json
{
  "message": "Chat functionality will be implemented in STEP 4"
}
```

---

## Admin Endpoints

### 12. Create User
**POST** `/admin/users`

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:** Same as register endpoint

**Response (201):** User object

---

### 13. List All Users
**GET** `/admin/users`

**Headers:** `Authorization: Bearer <admin_token>`

**Response (200):** Array of user objects

---

### 14. Register Patient
**POST** `/admin/patients`

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "email": "patient@example.com",
  "password": "temppass123",
  "full_name": "Jane Doe",
  "phone": "1234567890",
  "patient_number": "P001",
  "date_of_birth": "1990-05-15",
  "gender": "female",
  "assigned_doctor_id": 1,  // optional
  "medical_history": "No known allergies",  // optional
  "ward": "ICU",  // optional
  "bed_number": "A-101"  // optional
}
```

**Response (201):** Patient object with full details

---

### 15. Create Doctor Profile
**POST** `/admin/doctors/{user_id}`

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "specialization": "Cardiology",
  "license_number": "MD12345",
  "department": "Emergency"
}
```

**Response (201):**
```json
{
  "message": "Doctor profile created successfully",
  "doctor_id": 1
}
```

---

### 16. Create Nurse Profile
**POST** `/admin/nurses/{user_id}`

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "ward_assigned": "ICU",
  "shift": "morning"  // morning | evening | night
}
```

**Response (201):**
```json
{
  "message": "Nurse profile created successfully",
  "nurse_id": 1
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access forbidden. Required roles: ['admin']"
}
```

### 404 Not Found
```json
{
  "detail": "Patient not found or not assigned to you"
}
```

---

## Future Endpoints (STEP 2+)

These will be implemented in later steps:

```
POST   /api/vitals              # Edge device sends vitals data
POST   /api/alert               # Edge device sends alert
PUT    /api/doctor/alerts/{id}/ack  # Acknowledge alert
PUT    /api/nurse/alerts/{id}/ack   # Acknowledge alert
```
