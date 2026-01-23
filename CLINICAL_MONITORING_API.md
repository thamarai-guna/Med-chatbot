# Clinical Monitoring System - API Guide

## ⚠️ CRITICAL PRECONDITION

**Before ANY symptom monitoring or clinical assessment:**

Medical reports MUST be uploaded and available for the patient.

If no medical report exists:
- Symptom monitoring is BLOCKED
- Chat is BLOCKED
- Risk assessment is BLOCKED
- Response: `"Medical reports are required before symptom monitoring can begin."`

---

## Overview

This is a **POST-DISCHARGE NEUROLOGICAL PATIENT MONITORING** system. It is NOT a general chatbot—it is a clinical monitoring assistant designed to follow strict medical guidelines.

## Core Principles

### Knowledge Sources (STRICT)

**SOURCE 1: MEDICAL KNOWLEDGE (PRIMARY)**
- Brain-related medical books and clinical guidelines
- Stored in vector database (Retrieval-Augmented Generation)
- Accessed ONLY via RAG
- System does NOT use external medical knowledge

**SOURCE 2: PATIENT CONTEXT (SECONDARY)**
- Patient medical reports and daily responses
- Used only to understand symptoms, history, medications, risk factors
- NOT treated as medical knowledge

### Core Responsibilities

1. Generate symptom monitoring questions
2. Adapt questions based on patient report and previous answers
3. Avoid repeated questions
4. Assess patient risk using retrieved medical guidance
5. Output structured results (JSON only)

---

## API Endpoints

### 0. Check Patient Report Status (MANDATORY FIRST)

**Endpoint:** `GET /api/patient/{patient_id}/report/status`

**Response - Report Available:**
```json
{
  "patient_id": "P001",
  "has_report": true,
  "valid": true,
  "message": "Medical report verified. Monitoring can proceed.",
  "can_proceed_with_monitoring": true
}
```

**Response - No Report:**
```json
{
  "patient_id": "P001",
  "has_report": false,
  "valid": false,
  "message": "Medical reports are required before symptom monitoring can begin.",
  "can_proceed_with_monitoring": false
}
```

**ALWAYS check this first before attempting any monitoring or chat operations.**

---

### 1. Start Monitoring Session

**Endpoint:** `POST /api/monitoring/session/start`

**Request:**
```json
{
  "patient_id": "P001",
  "max_questions": 6
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "max_questions": 6,
  "message": "Monitoring session started. Ready for first question."
}
```

---

### 2. Get Next Question

**Endpoint:** `POST /api/monitoring/session/{session_id}/next-question`

**Response:**
```json
{
  "patient_id": "P001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "Have you experienced any weakness or numbness in your arms or legs since discharge?",
  "answer_type": "YES_NO",
  "question_number": 1,
  "total_expected": 6
}
```

**Answer Types:**
- `YES_NO` - Simple yes/no answers
- `SCALE_0_10` - Severity scale (0=none, 10=worst)
- `SHORT_TEXT` - Brief text (max 10-15 words, rare use)

---

### 3. Submit Answer

**Endpoint:** `POST /api/monitoring/session/{session_id}/submit-answer`

**Request:**
```json
{
  "patient_id": "P001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "Have you experienced any weakness or numbness in your arms or legs since discharge?",
  "answer": "YES",
  "answer_type": "YES_NO"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_recorded": "Have you experienced any weakness or numbness in your arms or legs since discharge?",
  "message": "Answer recorded. Ready for next question."
}
```

---

### 4. Get Final Assessment

**Endpoint:** `POST /api/monitoring/session/{session_id}/assessment`

**Response:**
```json
{
  "patient_id": "P001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_level": "LOW",
  "reason": [
    "No new neurological symptoms reported",
    "Symptoms remain stable compared to previous check-in"
  ],
  "action": "You are doing well. Continue your normal routine and take your prescribed medicines.",
  "total_questions_asked": 5,
  "timestamp": "2025-01-23T14:30:45.123456"
}
```

---

### 5. Check Session Status

**Endpoint:** `GET /api/monitoring/session/{session_id}`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "status": "complete|active",
  "questions_asked": 5,
  "max_questions": 6,
  "created_at": "2025-01-23T14:15:00.000000",
  "completed_at": "2025-01-23T14:30:45.123456",
  "assessment": { ... }
}
```

---

## Question Generation Rules

### STRICT Rules

- Ask ONE question at a time
- Each question EXACTLY ONE LINE
- Use simple, patient-friendly language
- Focus ONLY on neurological symptoms

### Question Limits

- **Minimum:** 3 questions
- **Maximum:** 6 questions
- Stop early if symptoms are stable

### Allowed Question Areas

- Speech or confusion
- Headache or pain
- Dizziness or balance
- Weakness or numbness
- Vision problems
- Seizure activity (only if present in patient report)
- Medication intake
- Daily functioning

### Anti-Repetition Rules

- Never repeat the same question in one session
- Do NOT re-ask symptoms answered as NO
- Re-ask ONLY if:
  - Symptom worsened
  - New related symptom appears
  - Medical guidance requires follow-up

---

## Risk Assessment Rules

### Risk Levels (STRICT - Choose ONE)

- **LOW:** No concerning symptoms, stable condition, normal activities safe
- **MEDIUM:** Some symptoms present but manageable, needs monitoring
- **HIGH:** Serious symptoms present, requires urgent medical attention

**Note:** CRITICAL is NOT used in this system. Use HIGH for life-threatening cases.

### Assessment Logic

Use ONLY:
- Patient responses
- Patient report
- Retrieved medical guidance (RAG)

Analyze:
- Severity
- Trend
- Symptom combinations

### Risk Assessment Output

```json
{
  "risk_level": "LOW|MEDIUM|HIGH",
  "reason": [
    "Bullet point 1",
    "Bullet point 2"
  ],
  "action": "Patient-friendly action recommendation"
}
```

---

## Action Recommendations

### IF Risk Level is HIGH
- Advise visiting doctor or nearest hospital immediately
- Encourage contacting caregiver or family
- NO medication advice

### IF Risk Level is MEDIUM
- Advise continuing prescribed medicines
- Encourage rest and monitoring
- NO new medicines or dosage changes

### IF Risk Level is LOW
- Reassure calmly
- Encourage normal routine and prescribed medicines

---

## Reason Output Rules

- Use bullet points (1–3 bullets)
- Simple language
- Based on retrieved guidance + patient responses
- NO diagnosis
- NO source references
- NO medical jargon

---

## Safety Rules (MANDATORY)

1. Do NOT diagnose diseases
2. Do NOT prescribe or change medicines
3. Do NOT replace a doctor
4. Always prioritize patient safety
5. Return ONLY JSON (no markdown, no explanations)
6. No text outside JSON responses

---

## Complete Monitoring Session Example

### Step 1: Start Session
```bash
curl -X POST http://localhost:8000/api/monitoring/session/start \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P001", "max_questions": 5}'
```

### Step 2-N: Get Question and Submit Answer (Loop)
```bash
# Get question
curl -X POST http://localhost:8000/api/monitoring/session/{session_id}/next-question

# Submit answer
curl -X POST http://localhost:8000/api/monitoring/session/{session_id}/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "session_id": "{session_id}",
    "question": "Have you had any headaches?",
    "answer": "NO",
    "answer_type": "YES_NO"
  }'

# Repeat until complete or max questions reached
```

### Step N+1: Get Final Assessment
```bash
curl -X POST http://localhost:8000/api/monitoring/session/{session_id}/assessment
```

---

## Session Lifecycle

```
1. START SESSION
   ↓
2. GET QUESTION → SUBMIT ANSWER (repeat 3-6 times)
   ↓
3. GET ASSESSMENT (final risk level + action)
   ↓
4. SESSION COMPLETE
```

---

## Error Handling

### Common Errors

| Status | Message | Solution |
|--------|---------|----------|
| 404 | Session not found | Invalid session_id |
| 400 | Session is not active | Session already completed |
| 400 | Invalid answer type | Use YES_NO, SCALE_0_10, or SHORT_TEXT |
| 400 | YES_NO answer must be YES or NO | Check answer format |
| 400 | SCALE answer must be 0-10 | Ensure numeric value 0-10 |
| 500 | Failed to generate valid question | LLM error, retry |

---

## Frontend Integration Example (React)

```javascript
// Start session
const startSession = async (patientId) => {
  const res = await fetch('http://localhost:8000/api/monitoring/session/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patient_id: patientId, max_questions: 5 })
  });
  return res.json();
};

// Get next question
const getQuestion = async (sessionId) => {
  const res = await fetch(`http://localhost:8000/api/monitoring/session/${sessionId}/next-question`, {
    method: 'POST'
  });
  return res.json();
};

// Submit answer
const submitAnswer = async (sessionId, question, answer, answerType) => {
  const res = await fetch(`http://localhost:8000/api/monitoring/session/${sessionId}/submit-answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      patient_id: patientId,
      session_id: sessionId,
      question,
      answer,
      answer_type: answerType
    })
  });
  return res.json();
};

// Get assessment
const getAssessment = async (sessionId) => {
  const res = await fetch(`http://localhost:8000/api/monitoring/session/${sessionId}/assessment`, {
    method: 'POST'
  });
  return res.json();
};
```

---

## Patient Experience Flow

1. **Login** → Patient authenticates
2. **Start Monitoring** → Click "Daily Check-in"
3. **Questions** → Answer 3-6 questions about neurological symptoms
4. **Assessment** → Receive risk assessment and recommendations
5. **Confirmation** → "Thank you. That's all for today's check-in."

---

## Demo Credentials

- **Patient:** `patient1` / Password: `pass123`
- **Doctor:** `doctor1` / Password: `pass123`
- **Nurse:** `nurse1` / Password: `pass123`

---

## Architecture

```
Frontend (React) → API Gateway → Backend (FastAPI)
                                    ↓
                              LLM (Groq) → Question/Assessment
                                    ↓
                          RAG Engine → Medical Knowledge
                                    ↓
                          Patient Manager → History
```

---

## Support

For issues or questions about the clinical monitoring system, refer to the clinical guidelines document or contact the medical team.

**Last Updated:** January 23, 2026
