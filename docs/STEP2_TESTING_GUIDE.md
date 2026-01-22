# STEP 2 Testing Guide - Alert System

This guide covers end-to-end testing of the Alert Ingestion and Display functionality implemented in STEP 2.

## Prerequisites

Before testing, ensure:
1. PostgreSQL database is running and configured
2. Backend server is started (`uvicorn app.main:app --reload`)
3. Frontend dev server is running (`npm start`)
4. Demo users are seeded in the database
5. At least one patient is assigned to a doctor

## Test Environment Setup

### 1. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

The server should start on `http://localhost:8000`. Verify the alert endpoint is registered:
- Navigate to `http://localhost:8000/docs`
- Confirm `/api/alerts` endpoints are listed

### 2. Start Frontend Server

```bash
cd frontend
npm install
npm start
```

The React app should open at `http://localhost:3000`.

### 3. Verify Environment Variables

Check `backend/.env`:
```
EDGE_DEVICE_API_KEY=your-secret-edge-api-key-here
```

## Test Scenarios

### Test 1: Edge Device Alert Ingestion

**Objective:** Verify edge devices can POST alerts to the backend.

**Steps:**
1. Open terminal and navigate to `edge_devices/`
2. Run: `python send_alert.py`
3. Select option 1 (Vitals Alert) or 2 (Coma Alert)
4. Observe the response

**Expected Result:**
- Script displays "Alert sent successfully!"
- Response includes alert ID and status "NEW"
- Backend logs show POST request to `/api/alerts`

**Validation:**
- Check database: `SELECT * FROM alerts ORDER BY created_at DESC LIMIT 1;`
- Alert should have status="NEW" and correct patient_id

### Test 2: Alert Display in Doctor Dashboard

**Objective:** Verify doctors can see alerts for their assigned patients.

**Steps:**
1. Login to frontend with doctor credentials (`doctor@hospital.com` / `doctor123`)
2. Navigate to "Alerts" tab
3. Observe the alerts panel

**Expected Result:**
- Alerts are displayed in cards with correct severity colors
- Alert shows patient name, patient number, alert type, message, timestamp
- Only alerts for doctor's assigned patients are visible
- NEW alerts have blue left border

**Validation:**
- Send alert for patient assigned to logged-in doctor
- Refresh should happen automatically every 5 seconds
- Alert should appear without manual page refresh

### Test 3: Alert Display in Nurse Dashboard

**Objective:** Verify nurses can see alerts for patients in their ward.

**Steps:**
1. Login to frontend with nurse credentials (`nurse@hospital.com` / `nurse123`)
2. Navigate to "Active Alerts" tab
3. Observe the alerts panel

**Expected Result:**
- Alerts for all patients in nurse's ward are visible
- Alert cards match the same format as doctor's view
- Real-time polling updates every 5 seconds

### Test 4: Alert Acknowledgment

**Objective:** Verify users can acknowledge alerts.

**Steps:**
1. Login as doctor or nurse
2. Find an alert with status "NEW"
3. Click "Acknowledge" button
4. Observe the UI changes

**Expected Result:**
- Alert card changes from blue border to gray
- Status changes from "NEW" to "ACKNOWLEDGED"
- Acknowledged by name appears (e.g., "Acknowledged by Dr. Smith")
- "Acknowledge" button is replaced with checkmark icon

**Validation:**
- Check database: `SELECT * FROM alerts WHERE id = <alert_id>;`
- `status` should be "ACKNOWLEDGED"
- `acknowledged_by` should be user's ID
- `acknowledged_at` should have timestamp

### Test 5: Severity Color Coding

**Objective:** Verify alerts display with correct severity colors.

**Steps:**
1. Send alerts with different severities:
   - HIGH: Red background
   - MEDIUM: Yellow background
   - LOW: Green background
2. View in dashboard

**Expected Result:**
- High severity alerts have red badge (`#dc3545`)
- Medium severity alerts have yellow badge (`#ffc107`)
- Low severity alerts have green badge (`#28a745`)

### Test 6: Real-Time Polling

**Objective:** Verify automatic alert updates.

**Steps:**
1. Login to dashboard and keep it open
2. From another terminal, run `send_alert.py`
3. Send a new alert
4. Watch the dashboard (do NOT refresh manually)

**Expected Result:**
- New alert appears within 5 seconds
- No page refresh is required
- Poll interval should be visible in browser console logs

### Test 7: Alert Filtering

**Objective:** Verify filter functionality.

**Steps:**
1. Login to dashboard with multiple alerts
2. Use filter dropdown to select:
   - ALL
   - NEW
   - ACKNOWLEDGED

**Expected Result:**
- "NEW" shows only unacknowledged alerts
- "ACKNOWLEDGED" shows only acknowledged alerts
- "ALL" shows both types
- Filtering happens instantly without API call

### Test 8: Role-Based Access Control

**Objective:** Verify alerts are filtered by user role.

**Steps:**
1. Create patients in different wards
2. Assign Doctor A to Patient 1 (Ward A)
3. Assign Doctor B to Patient 2 (Ward B)
4. Send alerts for both patients
5. Login as Doctor A
6. Login as Doctor B (separate browser/incognito)

**Expected Result:**
- Doctor A sees only Patient 1's alerts
- Doctor B sees only Patient 2's alerts
- Nurses in Ward A see Patient 1's alerts
- Nurses in Ward B see Patient 2's alerts

### Test 9: Edge Device Authentication

**Objective:** Verify API key authentication for edge devices.

**Steps:**
1. Try sending alert WITHOUT X-API-Key header:
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
     -H "Content-Type: application/json" \
     -d '{"patient_id": 1, "alert_type": "VITALS_ABNORMAL", "message": "Test", "severity": "HIGH", "source": "vitals_edge"}'
   ```

2. Try with WRONG API key:
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
     -H "X-API-Key: wrong-key" \
     -H "Content-Type: application/json" \
     -d '{"patient_id": 1, "alert_type": "VITALS_ABNORMAL", "message": "Test", "severity": "HIGH", "source": "vitals_edge"}'
   ```

3. Try with CORRECT API key:
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
     -H "X-API-Key: your-secret-edge-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"patient_id": 1, "alert_type": "VITALS_ABNORMAL", "message": "Test", "severity": "HIGH", "source": "vitals_edge"}'
   ```

**Expected Result:**
- Request 1: Returns 401 Unauthorized
- Request 2: Returns 401 Unauthorized
- Request 3: Returns 200 OK with alert ID

### Test 10: Alert Types and Sources

**Objective:** Verify all alert types display correctly.

**Steps:**
1. Send alerts of each type:
   - VITALS_ABNORMAL (source: vitals_edge)
   - COMA_MOVEMENT_DETECTED (source: coma_edge)
   - HIGH_RISK_FROM_CHATBOT (source: ai_chatbot)
2. View in dashboard

**Expected Result:**
- Each alert displays with correct emoji prefix:
  - Vitals: 🩺
  - Coma: 🛏️
  - Chatbot: 💬
- Alert type is human-readable (e.g., "Vitals Abnormal")

## Performance Testing

### Load Test: Multiple Concurrent Alerts

**Steps:**
1. Run edge device simulator in loop mode:
   ```python
   # Modify send_alert.py to send 100 alerts
   for i in range(100):
       simulate_vitals_alert()
   ```
2. Monitor backend logs
3. Check database record count
4. Verify frontend displays all alerts

**Expected Result:**
- All 100 alerts are stored in database
- Frontend pagination/scrolling handles large lists
- No crashes or memory leaks

### Polling Performance

**Steps:**
1. Open browser DevTools -> Network tab
2. Login to dashboard
3. Monitor API requests to `/api/alerts`

**Expected Result:**
- Requests fire every 5 seconds
- Response time < 500ms
- No duplicate requests

## Error Handling Tests

### Test 11: Invalid Patient ID

**Steps:**
1. Send alert with non-existent patient_id:
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
     -H "X-API-Key: your-secret-edge-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"patient_id": 99999, "alert_type": "VITALS_ABNORMAL", "message": "Test", "severity": "HIGH", "source": "vitals_edge"}'
   ```

**Expected Result:**
- Returns 400 Bad Request or 404 Not Found
- Error message: "Patient not found"

### Test 12: Invalid Alert Type

**Steps:**
1. Send alert with invalid alert_type:
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
     -H "X-API-Key: your-secret-edge-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"patient_id": 1, "alert_type": "INVALID_TYPE", "message": "Test", "severity": "HIGH", "source": "vitals_edge"}'
   ```

**Expected Result:**
- Returns 422 Unprocessable Entity
- Error indicates enum validation failure

### Test 13: Network Error Handling

**Steps:**
1. Stop backend server
2. Login to frontend
3. Observe error messages

**Expected Result:**
- Dashboard shows "Failed to load alerts" message
- No frontend crashes
- Retry mechanism continues polling

## Database Verification

After tests, verify database state:

```sql
-- Check all alerts
SELECT 
  a.id,
  a.alert_type,
  a.severity,
  a.status,
  p.patient_number,
  u.full_name as acknowledged_by,
  a.created_at
FROM alerts a
JOIN patients p ON a.patient_id = p.id
LEFT JOIN users u ON a.acknowledged_by = u.id
ORDER BY a.created_at DESC;

-- Count alerts by status
SELECT status, COUNT(*) as count
FROM alerts
GROUP BY status;

-- Count alerts by severity
SELECT severity, COUNT(*) as count
FROM alerts
GROUP BY severity;
```

## Test Checklist

- [ ] Backend server starts without errors
- [ ] Alert model and migrations applied
- [ ] Edge device can POST alerts with API key
- [ ] Unauthorized requests are rejected
- [ ] Doctor sees only assigned patients' alerts
- [ ] Nurse sees only ward patients' alerts
- [ ] Alerts display with correct severity colors
- [ ] Acknowledge button changes alert status
- [ ] Real-time polling updates every 5 seconds
- [ ] Filter dropdown works (ALL/NEW/ACKNOWLEDGED)
- [ ] All alert types display correctly
- [ ] Patient details shown in alerts
- [ ] Timestamps are formatted correctly
- [ ] Frontend handles network errors gracefully
- [ ] Database records match UI display

## Common Issues and Solutions

### Issue 1: Alert Not Appearing in Dashboard

**Possible Causes:**
- Patient not assigned to logged-in doctor
- Nurse ward doesn't match patient's ward
- Alert status filter hiding the alert

**Solution:**
- Verify patient assignment in database
- Check filter is set to "ALL"
- Check browser console for API errors

### Issue 2: "Unauthorized" Error from Edge Device

**Possible Causes:**
- Missing X-API-Key header
- Wrong API key value
- API key not set in backend/.env

**Solution:**
- Verify EDGE_DEVICE_API_KEY in .env
- Restart backend server after .env changes
- Check send_alert.py has correct API key

### Issue 3: Polling Not Working

**Possible Causes:**
- JavaScript error in browser console
- useEffect dependency array incorrect
- Network tab shows no requests

**Solution:**
- Open browser DevTools -> Console
- Check for errors in AlertsPanel component
- Verify localStorage has valid JWT token

## Next Steps

After completing STEP 2 testing:
1. Document any bugs found
2. Update dev_memory.md with test results
3. Prepare for STEP 3 (if applicable)
4. Gather stakeholder feedback on alert UX
