# Medical Chatbot - Refactored Architecture

## 🏗️ **New File Structure**

```
Med-chatbot/
├── rag_engine.py              # ✨ NEW - Core RAG logic (Streamlit-independent)
├── falcon.py                  # 📝 REFACTORED - Document processing utilities only
├── chatbot_streamlit_combined.py  # 🎨 UPDATED - UI layer using rag_engine
├── test_rag_engine.py         # ✨ NEW - Test suite for rag_engine
├── requirements.txt
├── .env
├── .env.example
└── vector store/
    └── DefaultVectorDB/
```

---

## 📦 **Module Breakdown**

### **1. `rag_engine.py` - Core RAG Logic** ✨ NEW

**Purpose:** Streamlit-independent RAG engine for medical Q&A

**Classes:**
- `RAGEngine` - Main RAG engine with chat history and vector store integration

**Functions:**
- `answer_question(question, vector_store_name, context_docs, max_tokens) -> dict`
  - Returns: `{"answer": str, "risk_level": str, "risk_reason": str, "source_documents": list}`

**Features:**
- ✅ Groq LLM API integration
- ✅ FAISS vector store retrieval
- ✅ Chat history management (last 4 exchanges)
- ✅ **Medical risk assessment** (LOW/MEDIUM/HIGH)
- ✅ No Streamlit dependencies

**Usage:**
```python
from rag_engine import answer_question, RAGEngine

# Standalone function
result = answer_question("What is diabetes?", vector_store_name="DefaultVectorDB")
print(result["answer"])
print(f"Risk: {result['risk_level']}")

# Or use the class for persistent conversations
engine = RAGEngine(vector_store_name="DefaultVectorDB", max_tokens=500)
result = engine.answer_question("What is hypertension?")
```

---

### **2. `falcon.py` - Document Processing** 📝 REFACTORED

**Purpose:** Document ingestion and vector store management

**Functions:**
- `read_pdf(file)` - Extract text from PDF
- `read_txt(file)` - Read text files
- `split_doc(document, chunk_size, chunk_overlap)` - Split text into chunks
- `embedding_storing(split, create_new_vs, existing_vector_store, new_vs_name)` - Create/merge vector stores

**Changes:**
- ❌ Removed: `call_groq()`, `prepare_rag_llm()`, `generate_answer()`
- ✅ Kept: Document processing and vector store utilities
- ✅ Still used by Streamlit for document embedding page

---

### **3. `chatbot_streamlit_combined.py` - UI Layer** 🎨 UPDATED

**Purpose:** Streamlit demo interface

**Changes:**
- Now uses `RAGEngine` class from `rag_engine.py`
- Displays risk assessment with color-coded alerts:
  - 🚨 RED for HIGH risk
  - ⚠️ YELLOW for MEDIUM risk
  - ℹ️ BLUE for LOW risk
- Simplified initialization flow
- Source tracking includes risk information

**Functions:**
- `display_chatbot_page()` - Chat interface using RAGEngine
- `display_document_embedding_page()` - Document upload using falcon utilities

---

### **4. `test_rag_engine.py` - Test Suite** ✨ NEW

**Purpose:** Test RAG engine without Streamlit

**Tests:**
1. Standalone function test
2. RAGEngine class with chat history
3. Risk assessment validation

**Run:**
```bash
python test_rag_engine.py
```

---

## 🔄 **Migration Summary**

### **Before:**
```
falcon.py (80 lines)
├── Document processing
├── Groq API calls
├── RAG logic
└── Streamlit-dependent answer generation
```

### **After:**
```
rag_engine.py (250 lines)
├── RAGEngine class
├── Groq API integration
├── Risk assessment
└── Standalone answer_question()

falcon.py (50 lines)
├── Document processing only
└── Vector store utilities
```

---

## 🚀 **Usage Examples**

### **A. Streamlit Demo (Original)**
```bash
streamlit run chatbot_streamlit_combined.py
```

### **B. Python Script (NEW)**
```python
from rag_engine import RAGEngine

# Initialize once
engine = RAGEngine(
    vector_store_name="DefaultVectorDB",
    max_tokens=500,
    temperature=0.7
)

# Ask questions
result = engine.answer_question("What causes heart disease?")

print(f"Answer: {result['answer']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Sources: {len(result['source_documents'])} documents")
```

### **C. API Integration (Future)**
```python
from flask import Flask, request, jsonify
from rag_engine import RAGEngine

app = Flask(__name__)
engine = RAGEngine(vector_store_name="DefaultVectorDB")

@app.route("/ask", methods=["POST"])
def ask_question():
    question = request.json.get("question")
    result = engine.answer_question(question)
    return jsonify(result)
```

---

## 🎯 **Key Benefits**

✅ **Separation of Concerns**
- Core logic decoupled from UI
- Easy to test without Streamlit
- Can be used in APIs, CLIs, or other UIs

✅ **Reusability**
- `rag_engine.py` can be imported anywhere
- Standalone `answer_question()` function for quick usage
- `RAGEngine` class for persistent conversations

✅ **Medical Risk Assessment**
- Automatic risk level detection (HIGH/MEDIUM/LOW)
- Context-aware reasoning
- Helps prioritize urgent cases

✅ **Maintainability**
- Clear module boundaries
- Easier to add features (e.g., multi-patient support)
- Testing without UI dependencies

---

## 🔧 **Setup (Same as Before)**

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable:
```bash
# .env file
GROQ_API_KEY=your_key_here
```

3. Run Streamlit demo:
```bash
streamlit run chatbot_streamlit_combined.py
```

4. Or test core engine:
```bash
python test_rag_engine.py
```

---

## 📋 **Next Steps for Hospital Project**

Now that core logic is separated, you can easily add:

1. **Multi-Patient Support**
   - Add patient_id parameter to RAGEngine
   - Separate chat histories per patient

2. **Medical Records Integration**
   - Load patient-specific documents
   - Create patient-specific vector stores

3. **API Endpoints**
   - Flask/FastAPI wrapper around rag_engine
   - REST API for external systems

4. **Risk Prediction Model**
   - Enhance risk assessment with ML model
   - Integrate with hospital triage system

All of these can be done by extending `rag_engine.py` without touching Streamlit!
