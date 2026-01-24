"""
Quick Usage Example - Medical Chatbot RAG Engine
"""

from rag_engine import RAGEngine
from patient_manager import get_patient_manager
import os

# Register a test patient
pm = get_patient_manager()
test_patient_id = "test_patient_v1"
pm.register_patient(
    patient_id=test_patient_id,
    name="Test Patient",
    email="test@example.com",
    age=30,
    medical_history="Hypertension, Diabetes Type 2"
)
print(f"Registered/ensured patient {test_patient_id}")

# Example 1: Simple Q&A
print("Example 1: Basic Question\n" + "="*50)
try:
    engine = RAGEngine(patient_id=test_patient_id, max_tokens=300)
    result = engine.answer_question("What is diabetes?")

    print(f"Q: What is diabetes?")
    print(f"A: {result['answer']}")
    print(f"\nRisk Level: {result['risk_level']}")
    print(f"Risk Reason: {result['risk_reason']}\n")
except Exception as e:
    print(f"Error in Example 1: {e}")


# Example 2: Multiple Questions with Context
print("\nExample 2: Conversation with History\n" + "="*50)
try:
    engine2 = RAGEngine(patient_id=test_patient_id, max_tokens=300)

    questions = [
        "What causes high blood pressure?",
        "What are the symptoms?",
        "How can it be treated?"
    ]

    for q in questions:
        result = engine2.answer_question(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer'][:150]}...")
        print(f"Risk: {result['risk_level']}")
except Exception as e:
    print(f"Error in Example 2: {e}")


# Example 3: Risk Assessment
print("\n\nExample 3: Risk Assessment\n" + "="*50)
try:
    high_risk_q = "I'm having severe chest pain and difficulty breathing"
    result = engine.answer_question(high_risk_q)

    print(f"Q: {high_risk_q}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Reason: {result['risk_reason']}")
except Exception as e:
    print(f"Error in Example 3: {e}")


# Example 4: Standalone Function (No Class)
print("\n\nExample 4: Standalone Function\n" + "="*50)
try:
    from rag_engine import answer_question
    
    result = answer_question(
        question="What vitamins are important for health?",
        patient_id=test_patient_id,
        max_tokens=200
    )

    print(f"Answer: {result['answer']}")
    print(f"\nHistory: {len(result['source_documents'])} source documents used")
except Exception as e:
    print(f"Error in Example 4: {e}")
