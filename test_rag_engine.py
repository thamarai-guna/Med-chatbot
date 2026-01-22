"""
Simple test script for RAG Engine (Streamlit-independent)
"""

from rag_engine import answer_question, RAGEngine
import os
from dotenv import load_dotenv

load_dotenv()

def test_standalone_function():
    """Test the standalone answer_question function"""
    print("=" * 60)
    print("TEST 1: Standalone Function")
    print("=" * 60)
    
    question = "What are the symptoms of diabetes?"
    
    try:
        result = answer_question(
            question=question,
            vector_store_name="DefaultVectorDB",
            max_tokens=300
        )
        
        print(f"\n📝 Question: {question}")
        print(f"\n💬 Answer:\n{result['answer']}\n")
        print(f"⚠️  Risk Level: {result['risk_level']}")
        print(f"📋 Risk Reason: {result['risk_reason']}")
        print(f"\n📚 Sources: {len(result['source_documents'])} documents retrieved")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_rag_engine_class():
    """Test the RAGEngine class with conversation history"""
    print("\n" + "=" * 60)
    print("TEST 2: RAGEngine Class (with chat history)")
    print("=" * 60)
    
    try:
        # Initialize engine
        engine = RAGEngine(
            vector_store_name="DefaultVectorDB",
            max_tokens=300,
            temperature=0.7
        )
        
        # Ask first question
        question1 = "What is hypertension?"
        result1 = engine.answer_question(question1)
        
        print(f"\n📝 Question 1: {question1}")
        print(f"💬 Answer: {result1['answer'][:200]}...")
        print(f"⚠️  Risk: {result1['risk_level']}")
        
        # Ask follow-up question (should use history)
        question2 = "What are the treatment options?"
        result2 = engine.answer_question(question2)
        
        print(f"\n📝 Question 2 (follow-up): {question2}")
        print(f"💬 Answer: {result2['answer'][:200]}...")
        print(f"⚠️  Risk: {result2['risk_level']}")
        
        # Display chat history
        print(f"\n📜 Chat History: {len(engine.get_history())} exchanges")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_risk_assessment():
    """Test risk assessment with different question types"""
    print("\n" + "=" * 60)
    print("TEST 3: LLM-Based Risk Assessment")
    print("=" * 60)
    
    test_questions = [
        ("What is a healthy diet?", "Expected: LOW"),
        ("I have a mild headache", "Expected: LOW or MEDIUM"),
        ("I've had chest pain for 2 hours", "Expected: HIGH"),
        ("My father collapsed and isn't breathing", "Expected: CRITICAL"),
        ("I have numbness in my left arm and confusion", "Expected: HIGH or CRITICAL"),
    ]
    
    try:
        engine = RAGEngine(vector_store_name="DefaultVectorDB", max_tokens=200)
        
        for question, expected in test_questions:
            result = engine.answer_question(question)
            print(f"\n📝 Q: {question}")
            print(f"⚠️  Risk: {result['risk_level']} ({expected})")
            print(f"📋 Reason: {result['risk_reason']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n🏥 Medical Chatbot RAG Engine - Test Suite\n")
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        exit(1)
    
    print("✅ GROQ_API_KEY found\n")
    
    # Run tests
    test_standalone_function()
    test_rag_engine_class()
    test_risk_assessment()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
