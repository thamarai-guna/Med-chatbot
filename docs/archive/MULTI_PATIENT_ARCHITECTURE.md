# Multi-Patient Medical Chatbot - Architecture & Schema

## Overview
Extended Med-chatbot to support multiple patients with complete data isolation, separate chat histories, and GDPR-compliant patient management.

---

## Database Schema

### SQLite Database: `patient_data.db`

```sql
-- Patients Table: Core patient information
CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,           -- Unique identifier (P001, patient_123, etc)
    name TEXT NOT NULL,                    -- Patient name
    email TEXT UNIQUE,                     -- Email (optional, unique)
    age INTEGER,                           -- Age (optional)
    medical_history TEXT,                  -- Medical background notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat History Table: Per-patient conversation records
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,              -- Foreign key to patients
    question TEXT NOT NULL,                -- User question
    answer TEXT NOT NULL,                  -- LLM answer
    risk_level TEXT,                       -- LOW|MEDIUM|HIGH|CRITICAL
    risk_reason TEXT,                      -- Explanation of risk level
    source_documents TEXT,                 -- JSON array of source docs
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Risk Assessments Table: Medical audit trail
CREATE TABLE risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,              -- Foreign key to patients
    question TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    risk_reason TEXT,
    context TEXT,                          -- Retrieved context
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);
```

### Key Features
- **Cascading Deletes**: Deleting a patient automatically deletes all their records (GDPR)
- **Data Isolation**: patient_id enforced on all queries
- **Audit Trail**: All risk assessments timestamped for medical compliance
- **Performance**: Indexed by patient_id for fast retrieval

---

## Module Architecture

### 1. `patient_manager.py` (NEW)
**Purpose**: Patient database management with complete isolation

```python
class PatientManager:
    # Core Methods
    def register_patient(patient_id, name, email, age, medical_history) → Dict
    def get_patient(patient_id) → Optional[Dict]
    def get_all_patients() → List[Dict]
    
    # Chat History Management
    def save_chat_message(patient_id, question, answer, risk_level, risk_reason, source_docs) → bool
    def get_patient_history(patient_id, limit=10) → List[Dict]
    
    # Risk Tracking
    def get_patient_risk_summary(patient_id, days=30) → Dict
    
    # GDPR Compliance
    def clear_patient_history(patient_id) → bool
    def delete_patient(patient_id) → bool
```

**Security Features**:
- patient_id validation on all operations
- Automatic timestamp tracking
- Cascade deletion for GDPR compliance

---

### 2. `rag_engine.py` (MODIFIED)
**Changes**: Added mandatory patient_id parameter

```python
class RAGEngine:
    def __init__(self, vector_store_name: str, patient_id: str, 
                 max_tokens: int = 500, temperature: float = 0.7):
        """
        BREAKING CHANGE: patient_id is now mandatory!
        Raises ValueError if patient_id is missing or invalid
        """
        if not patient_id:
            raise ValueError("patient_id is mandatory")
        
        self.patient_id = patient_id
        self.patient_manager = get_patient_manager()
        
        # Verify patient exists
        patient = self.patient_manager.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Load patient's previous chat history
        self._load_patient_history()
```

**Key Changes**:

1. **Constructor**:
   - Added `patient_id` parameter (MANDATORY)
   - Patient validation on initialization
   - Auto-loads patient's chat history

2. **Chat History Loading**:
   ```python
   def _load_patient_history(self):
       """Load patient's previous chat history from database"""
       history = self.patient_manager.get_patient_history(self.patient_id, limit=50)
       self.chat_history = [
           {"question": h["question"], "answer": h["answer"], ...}
           for h in history
       ]
   ```

3. **Answer Persistence**:
   ```python
   def answer_question(self, question: str) → Dict:
       # ... generate answer ...
       
       # Save to patient database (automatic)
       self.patient_manager.save_chat_message(
           patient_id=self.patient_id,
           question=question,
           answer=answer,
           risk_level=risk_assessment["risk_level"],
           risk_reason=risk_assessment["risk_reason"],
           source_documents=source_documents
       )
       return response
   ```

---

### 3. `chatbot_multi_patient.py` (NEW)
**Purpose**: Multi-patient Streamlit UI with patient management

**Features**:

1. **Patient Registration**:
   - Sidebar form for new patient registration
   - Fields: ID, Name, Email, Age, Medical History
   - Validation and duplicate detection

2. **Patient Selection**:
   - Dropdown to select from existing patients
   - Automatic history loading
   - Patient info display (name, ID, risk summary)

3. **Separate Chat Interfaces**:
   - Per-patient chat history
   - Patient-specific vector stores
   - Isolated conversation contexts

4. **Risk Tracking Dashboard**:
   - Risk distribution (last 30 days)
   - Max risk level alert
   - Query count tracking

---

## Data Flow

### Chat Flow (Per Patient)
```
User Input
    ↓
[Patient Verification] → Check patient_id exists
    ↓
[Load Context] → Load last 50 chat messages from patient_id
    ↓
[Retrieve Documents] → Query vector store for relevant docs
    ↓
[Generate Answer] → Call Groq LLM with context + history
    ↓
[Assess Risk] → LLM-based risk assessment
    ↓
[Save to DB] → Store in chat_history table with patient_id
    ↓
[Return Response] → Display with risk level + source docs
```

### Patient Isolation
```
Patient A requests chat    Patient B requests chat
        ↓                          ↓
    patient_id=P001         patient_id=P002
        ↓                          ↓
  Load history              Load history
  FROM chat_history         FROM chat_history
  WHERE patient_id='P001'   WHERE patient_id='P002'
        ↓                          ↓
  [Completely separate contexts - no cross-contamination]
```

---

## Migration from Single to Multi-Patient

### OLD Code (Single Patient)
```python
from rag_engine import RAGEngine

# No patient tracking
engine = RAGEngine(vector_store_name="medical_docs")
response = engine.answer_question("What is diabetes?")
```

### NEW Code (Multi-Patient)
```python
from rag_engine import RAGEngine
from patient_manager import get_patient_manager

pm = get_patient_manager()

# Register patient
pm.register_patient(
    patient_id="P001",
    name="John Doe",
    email="john@hospital.com",
    age=45
)

# Create engine with patient context
engine = RAGEngine(
    vector_store_name="medical_docs",
    patient_id="P001"  # MANDATORY
)

# Answer is automatically saved to patient history
response = engine.answer_question("What is diabetes?")

# Later - retrieve patient history
history = pm.get_patient_history("P001")
```

---

## Usage Examples

### Example 1: Register and Chat
```python
from patient_manager import get_patient_manager
from rag_engine import RAGEngine

pm = get_patient_manager()

# Register
pm.register_patient("P001", "Alice Smith", "alice@hospital.com", 52)

# Create engine
engine = RAGEngine("medical_docs", patient_id="P001")

# Chat
result = engine.answer_question("symptoms of cardiac arrhythmia")
print(f"Risk Level: {result['risk_level']}")

# Check history
history = pm.get_patient_history("P001")
print(f"Previous queries: {len(history)}")
```

### Example 2: Risk Summary
```python
pm = get_patient_manager()
summary = pm.get_patient_risk_summary("P001", days=30)

print(f"CRITICAL: {summary['risk_distribution']['CRITICAL']}")
print(f"HIGH: {summary['risk_distribution']['HIGH']}")
print(f"Max Risk: {summary['max_risk_level']}")
```

### Example 3: GDPR Compliance
```python
pm = get_patient_manager()

# Delete all patient data (cascading delete)
pm.delete_patient("P001")
# → Deletes: patient record + chat_history + risk_assessments
```

---

## Security Features

### Data Isolation
- ✅ patient_id validation on every database query
- ✅ Separate chat histories per patient
- ✅ No cross-patient data leakage

### Access Control
- ✅ Patient verification before RAGEngine initialization
- ✅ Patient ID checked on every chat message save
- ✅ History retrieval filtered by patient_id

### GDPR Compliance
- ✅ Cascading deletes (delete patient = delete all their data)
- ✅ Right to be forgotten implemented
- ✅ Audit trail with timestamps
- ✅ Optional patient anonymization

### Audit Trail
- ✅ All risk assessments timestamped
- ✅ Question/answer history preserved
- ✅ Track patient access times

---

## Running the New System

### Start Multi-Patient Bot
```bash
streamlit run chatbot_multi_patient.py
```

### Features in UI
1. **Sidebar**: Patient registration & selection
2. **Patient Info**: Name, ID, risk summary
3. **Chat Tab**: Conversation with patient history
4. **Documents Tab**: Upload documents (shared knowledge base)
5. **History Tab**: View all previous queries & assessments

---

## Database Queries Reference

### Find all HIGH/CRITICAL risk patients (medical alert)
```sql
SELECT DISTINCT p.patient_id, p.name, ch.risk_level, COUNT(*) as count
FROM patients p
JOIN chat_history ch ON p.patient_id = ch.patient_id
WHERE ch.risk_level IN ('HIGH', 'CRITICAL')
  AND ch.timestamp > datetime('now', '-7 days')
GROUP BY p.patient_id
ORDER BY count DESC;
```

### Patient activity report
```sql
SELECT p.patient_id, p.name, 
       COUNT(ch.id) as total_queries,
       COUNT(CASE WHEN ch.risk_level='CRITICAL' THEN 1 END) as critical_count
FROM patients p
LEFT JOIN chat_history ch ON p.patient_id = ch.patient_id
GROUP BY p.patient_id
ORDER BY total_queries DESC;
```

---

## Roadmap

### Phase 1 (Done) ✅
- Patient registration & management
- Separate chat histories
- Risk tracking
- GDPR compliance

### Phase 2 (Future)
- Patient medical records upload
- Drug interaction checking per patient
- Appointment scheduling integration
- Multi-language support

### Phase 3 (Future)
- Authentication/login
- Doctor assignments per patient
- Prescription history
- Insurance integration

---

## Testing Checklist

- [ ] Register Patient A
- [ ] Register Patient B  
- [ ] Chat with Patient A (verify history saves)
- [ ] Switch to Patient B (verify separate history)
- [ ] Verify Patient A history unchanged
- [ ] Test CRITICAL risk detection
- [ ] Delete Patient A (verify cascading delete)
- [ ] Verify Patient A data gone, Patient B intact

---

## Breaking Changes

⚠️ **Important**: The update requires changing existing code

**OLD**:
```python
engine = RAGEngine("vector_store_name")
```

**NEW** (required):
```python
engine = RAGEngine("vector_store_name", patient_id="P001")
```

**Migration**: Update all RAGEngine instantiations to include patient_id
