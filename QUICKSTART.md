# Quick Start Guide - STEP 2 Alert System

This guide will get you up and running with the alert system in 5 minutes.

## Prerequisites Checklist
- [ ] PostgreSQL installed and running
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Git repository cloned

---

## Step 1: Database Setup (2 minutes)

```bash
# Open PostgreSQL terminal
psql -U postgres

# Create database
CREATE DATABASE med_chatbot;

# Exit
\q
```

---

## Step 2: Backend Setup (1 minute)

```bash
# Navigate to backend
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env

# IMPORTANT: Edit .env file with your database credentials
# DATABASE_URL=postgresql://postgres:your_password@localhost/med_chatbot
# EDGE_DEVICE_API_KEY=hackathon-edge-api-key-2026

# Start backend server
uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Keep this terminal open.

---

## Step 3: Frontend Setup (1 minute)

Open a **new terminal:**

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start React app
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view the app in the browser.

  Local:            http://localhost:3000
```

Browser should automatically open. Keep this terminal open.

---

## Step 4: Seed Demo Data (30 seconds)

Open a **new terminal:**

```bash
cd backend
venv\Scripts\activate  # Activate virtual environment

# Run seed script (if available)
python scripts/seed_demo_data.py
```

**Manual Seeding via API:**

If seed script doesn't exist, visit http://localhost:8000/docs and use the Swagger UI:

1. Create Admin User:
   - POST `/api/auth/register`
   - Body: `{"email": "admin@hospital.com", "password": "admin123", "full_name": "Admin User", "role": "admin"}`

2. Login as Admin:
   - POST `/api/auth/login`
   - Copy the `access_token`

3. Click "Authorize" button in Swagger UI, paste token

4. Create Doctor:
   - POST `/api/admin/users` → Create user with role "doctor"
   - POST `/api/admin/doctors/{user_id}` → Create doctor profile

5. Create Patient:
   - POST `/api/admin/patients` → Create patient assigned to doctor

---

## Step 5: Test Alert Flow (1 minute)

Open a **new terminal:**

```bash
cd edge_devices

# Run alert simulator
python send_alert.py
```

**Expected Output:**
```
✅ Backend is reachable!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🏥 EDGE DEVICE ALERT SIMULATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Choose an option:
1. Send Vitals Alert (Simulated)
2. Send Coma Movement Alert (Simulated)
3. Send AI Chatbot Alert (Simulated)
4. Custom Alert
5. Exit

Enter your choice (1-5):
```

Choose option **1** to send a vitals alert.

---

## Step 6: View Alert in Dashboard (30 seconds)

1. Go to http://localhost:3000
2. Login with doctor credentials:
   - Email: `doctor@hospital.com`
   - Password: `doctor123`
3. Click on "🚨 Alerts" tab
4. You should see the alert appear within 5 seconds!

**Try These Actions:**
- Click "Acknowledge" button
- Watch the alert status change
- Send more alerts from the simulator
- Watch them auto-refresh

---

## Default Demo Credentials

If you seeded demo data, use these credentials:

| Role | Email | Password |
|------|-------|----------|
| Doctor | doctor@hospital.com | doctor123 |
| Nurse | nurse@hospital.com | nurse123 |
| Patient | patient@hospital.com | patient123 |
| Admin | admin@hospital.com | admin123 |

---

## Troubleshooting

### Backend won't start
**Error:** "Connection refused" or database error  
**Solution:**
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database `med_chatbot` exists

### Frontend won't start
**Error:** "npm ERR!"  
**Solution:**
- Delete `node_modules/` and `package-lock.json`
- Run `npm install` again
- Ensure Node.js 18+ is installed

### Edge device "Unauthorized"
**Error:** 401 Unauthorized when sending alert  
**Solution:**
- Check `EDGE_DEVICE_API_KEY` in `backend/.env`
- Restart backend after changing `.env`
- Verify API key in `send_alert.py` matches

### Alerts not appearing
**Error:** Dashboard shows "No alerts found"  
**Solution:**
- Check patient is assigned to logged-in doctor
- Verify alert was sent successfully (check `send_alert.py` output)
- Check browser console for errors (F12)
- Ensure filter is set to "ALL" in dashboard

### "Cannot read property of undefined" in browser
**Error:** React errors in console  
**Solution:**
- Ensure backend is running on port 8000
- Check localStorage has valid JWT token
- Logout and login again

---

## Quick Test Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Database created and accessible
- [ ] Demo users created
- [ ] Patient assigned to doctor
- [ ] Alert sent via simulator
- [ ] Alert appears in dashboard
- [ ] Acknowledge button works
- [ ] Auto-refresh working (5 seconds)

---

## Next Steps

✅ **System is working!** Now you can:

1. **Read Full Testing Guide:** `docs/STEP2_TESTING_GUIDE.md`
2. **Explore API:** http://localhost:8000/docs
3. **Test Multiple Users:** Open incognito windows for nurse/doctor
4. **Send Various Alerts:** Try all 3 types in simulator
5. **Check Database:** Use pgAdmin to inspect alerts table

---

## API Quick Reference

### Edge Device Alert
```bash
curl -X POST http://localhost:8000/api/alerts \
  -H "X-API-Key: hackathon-edge-api-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "alert_type": "VITALS_ABNORMAL",
    "message": "Heart rate: 120 bpm (above threshold)",
    "severity": "HIGH",
    "source": "vitals_edge"
  }'
```

### Get Alerts (Doctor)
```bash
curl -X GET http://localhost:8000/api/alerts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Acknowledge Alert
```bash
curl -X POST http://localhost:8000/api/alerts/1/acknowledge \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Support

If you encounter issues:
1. Check terminal logs for error messages
2. Inspect browser console (F12) for frontend errors
3. Review `docs/STEP2_TESTING_GUIDE.md` for detailed troubleshooting
4. Check `dev_memory.md` for project decisions

---

**🎉 Congratulations! Your alert system is running!**
