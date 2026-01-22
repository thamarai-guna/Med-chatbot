# 🏥 Medical Risk Assessment Prompts

## Overview
The chatbot now uses **LLM-based reasoning** (Groq API) to assess medical risk instead of simple keyword matching.

---

## 📋 System Prompt

**Location:** [rag_engine.py](rag_engine.py) - `_get_risk_assessment_system_prompt()`

```
You are a medical risk assessment AI for a hospital triage system. Your task is to evaluate medical queries and assign a risk level.

CRITICAL RULES:
1. You MUST respond with valid JSON only (no other text)
2. JSON format: {"risk_level": "LOW|MEDIUM|HIGH|CRITICAL", "risk_reason": "brief explanation"}
3. risk_reason must be 1-2 sentences maximum

RISK LEVEL DEFINITIONS:
- CRITICAL: Life-threatening emergencies requiring immediate intervention (cardiac arrest, severe trauma, stroke symptoms, major bleeding, loss of consciousness, severe breathing difficulty)
- HIGH: Urgent conditions needing prompt medical attention within hours (chest pain, acute severe symptoms, neurological changes, worsening symptoms over days)
- MEDIUM: Conditions requiring medical evaluation soon (persistent pain, fever, infections, new symptoms, chronic disease management)
- LOW: General health information, preventive care, mild symptoms, educational queries

RISK ESCALATION FACTORS:
- Symptoms worsening over multiple days → increase risk by 1 level
- Neurological red flags (confusion, vision changes, numbness, weakness) → HIGH or CRITICAL
- Cardiovascular symptoms (chest pain, palpitations with other symptoms) → HIGH or CRITICAL
- Breathing difficulty or severe pain → HIGH minimum
- Multiple concerning symptoms together → increase risk by 1 level
- Patient expressing distress or concern about severity → increase risk consideration

IMPORTANT: Consider the conversation history for progression of symptoms. If symptoms are recurring or worsening across multiple questions, this indicates higher risk.
```

---

## 💬 User Prompt Template

**Location:** [rag_engine.py](rag_engine.py) - `_create_risk_assessment_prompt()`

```
Assess the medical risk level for this patient interaction.

PATIENT QUESTION:
{question}

MEDICAL ANSWER PROVIDED:
{answer}

RELEVANT MEDICAL CONTEXT FROM DOCUMENTS:
{context[:800]}

CONVERSATION HISTORY (for symptom progression analysis):
{history}

Analyze the above information and respond with JSON only:
{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_reason": "Brief explanation (1-2 sentences max)"
}
```

---

## 🔧 API Configuration

**Model:** `llama-3.1-70b-versatile`  
**Temperature:** `0.3` (lower for consistent risk assessment)  
**Max Tokens:** `300`  
**Response Format:** `{"type": "json_object"}` (enforces JSON-only output)

---

## 📊 Risk Level Hierarchy

```
CRITICAL (🚨🚨)
├─ Life-threatening emergencies
├─ Requires immediate intervention
└─ Examples: cardiac arrest, severe trauma, stroke, major bleeding

HIGH (🚨)
├─ Urgent conditions
├─ Needs attention within hours
└─ Examples: chest pain, neurological changes, worsening symptoms

MEDIUM (⚠️)
├─ Requires evaluation soon
├─ Non-urgent but needs medical care
└─ Examples: persistent pain, fever, infections

LOW (ℹ️)
├─ General information
├─ Preventive care
└─ Examples: health education, mild symptoms
```

---

## 🎯 Context Used for Risk Assessment

1. **Current Question** - Patient's latest query
2. **Generated Answer** - Medical information provided
3. **Retrieved Documents** - Relevant medical context (up to 800 chars)
4. **Chat History** - Last 3 exchanges to detect symptom progression

---

## 📝 Example Risk Assessments

### Example 1: LOW Risk
**Question:** "What vitamins are good for bone health?"  
**Response:**
```json
{
  "risk_level": "LOW",
  "risk_reason": "Educational query about preventive health with no acute symptoms."
}
```

### Example 2: MEDIUM Risk
**Question:** "I've had a fever of 101°F for 2 days"  
**Response:**
```json
{
  "risk_level": "MEDIUM",
  "risk_reason": "Persistent fever lasting multiple days requires medical evaluation to rule out infection."
}
```

### Example 3: HIGH Risk
**Question:** "I have chest pain that comes and goes, started yesterday"  
**Response:**
```json
{
  "risk_level": "HIGH",
  "risk_reason": "Chest pain is a cardiovascular red flag requiring urgent evaluation within hours to rule out cardiac events."
}
```

### Example 4: CRITICAL Risk
**Question:** "My father collapsed and isn't responding, having trouble breathing"  
**Response:**
```json
{
  "risk_level": "CRITICAL",
  "risk_reason": "Loss of consciousness with breathing difficulty is life-threatening. Immediate emergency intervention required."
}
```

---

## 🔄 Progression Detection Example

**Conversation:**
1. User: "I have a headache"  
   → Risk: LOW

2. User: "The headache is worse today and I feel dizzy"  
   → Risk: MEDIUM (escalated due to worsening + new symptom)

3. User: "Now I'm having trouble seeing clearly"  
   → Risk: HIGH (neurological red flag + progression over days)

The LLM analyzes chat history to detect symptom progression and escalates risk accordingly.

---

## 🛡️ Fallback Mechanism

If the LLM API fails, the system falls back to keyword-based risk assessment:

```python
critical_keywords = ["cardiac arrest", "not breathing", "unconscious", ...]
high_risk_keywords = ["chest pain", "stroke", "heart attack", ...]
medium_risk_keywords = ["pain", "fever", "infection", ...]
```

This ensures the system always provides a risk assessment, even if the LLM is unavailable.

---

## 🎨 UI Display

**Streamlit Interface:**
- **CRITICAL:** 🚨🚨 Red error box + "CALL 911" warning
- **HIGH:** 🚨 Red error box + "Urgent care within hours"
- **MEDIUM:** ⚠️ Yellow warning box + "Evaluation recommended soon"
- **LOW:** ℹ️ Blue info box + Risk reason

---

## 📍 Code Locations

| Component | File | Function |
|-----------|------|----------|
| Risk Assessment Logic | [rag_engine.py](rag_engine.py#L107-L280) | `_assess_medical_risk()` |
| System Prompt | [rag_engine.py](rag_engine.py#L195-L220) | `_get_risk_assessment_system_prompt()` |
| User Prompt Template | [rag_engine.py](rag_engine.py#L222-L245) | `_create_risk_assessment_prompt()` |
| Fallback Logic | [rag_engine.py](rag_engine.py#L247-L280) | `_fallback_risk_assessment()` |
| UI Display | [chatbot_streamlit_combined.py](chatbot_streamlit_combined.py#L132-L148) | `display_chatbot_page()` |

---

## ✅ Key Features

✅ **LLM Reasoning** - Uses Groq API for intelligent risk assessment  
✅ **Context-Aware** - Considers question + answer + medical docs + chat history  
✅ **Progression Detection** - Identifies worsening symptoms over multiple messages  
✅ **Neurological Red Flags** - Auto-escalates for CNS symptoms  
✅ **JSON Response** - Structured output for reliable parsing  
✅ **Fallback Safety** - Keyword-based backup if LLM fails  
✅ **4-Level Risk Scale** - LOW/MEDIUM/HIGH/CRITICAL  

---

## 🚀 Usage in Code

```python
from rag_engine import RAGEngine

engine = RAGEngine(vector_store_name="DefaultVectorDB")

# Ask a question
result = engine.answer_question("I have chest pain")

# Access risk assessment
print(result["answer"])
print(f"Risk: {result['risk_level']}")
print(f"Reason: {result['risk_reason']}")

# Output:
# Risk: HIGH
# Reason: Chest pain is a cardiovascular red flag requiring urgent evaluation...
```

---

**Implementation Complete!** 🎉
