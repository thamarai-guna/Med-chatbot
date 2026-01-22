"""
Quick Usage Example - Medical Chatbot RAG Engine
"""

from rag_engine import RAGEngine

# Example 1: Simple Q&A
print("Example 1: Basic Question\n" + "="*50)
engine = RAGEngine(vector_store_name="DefaultVectorDB", max_tokens=300)
result = engine.answer_question("What is diabetes?")

print(f"Q: What is diabetes?")
print(f"A: {result['answer']}")
print(f"\nRisk Level: {result['risk_level']}")
print(f"Risk Reason: {result['risk_reason']}\n")


# Example 2: Multiple Questions with Context
print("\nExample 2: Conversation with History\n" + "="*50)
engine2 = RAGEngine(vector_store_name="DefaultVectorDB", max_tokens=300)

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


# Example 3: Risk Assessment
print("\n\nExample 3: Risk Assessment\n" + "="*50)
high_risk_q = "I'm having severe chest pain and difficulty breathing"
result = engine.answer_question(high_risk_q)

print(f"Q: {high_risk_q}")
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['risk_reason']}")


# Example 4: Standalone Function (No Class)
print("\n\nExample 4: Standalone Function\n" + "="*50)
from rag_engine import answer_question

result = answer_question(
    question="What vitamins are important for health?",
    vector_store_name="DefaultVectorDB",
    max_tokens=200
)

print(f"Answer: {result['answer']}")
print(f"\nHistory: {len(result['source_documents'])} source documents used")
