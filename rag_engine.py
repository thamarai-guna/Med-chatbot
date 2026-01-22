"""
RAG Engine - Core logic for medical chatbot
Streamlit-independent module for RAG-based question answering with Groq LLM API
"""

import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for medical Q&A
    """
    
    def __init__(self, vector_store_name: str, max_tokens: int = 500, temperature: float = 0.7):
        """
        Initialize RAG engine with vector store
        
        Args:
            vector_store_name: Name of the vector store folder
            max_tokens: Maximum tokens for LLM response
            temperature: LLM temperature (0.0-1.0)
        """
        self.vector_store_name = vector_store_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.chat_history = []
        self.retriever = None
        
        # Load vector store
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load FAISS vector store with embeddings"""
        try:
            instructor_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2", 
                model_kwargs={'device': 'cpu'}
            )
            
            loaded_db = FAISS.load_local(
                f"vector store/{self.vector_store_name}", 
                instructor_embeddings, 
                allow_dangerous_deserialization=True
            )
            
            self.retriever = loaded_db.as_retriever(search_kwargs={"k": 3})
            
        except Exception as e:
            raise RuntimeError(f"Failed to load vector store '{self.vector_store_name}': {str(e)}")
    
    def _call_groq(self, prompt: str) -> str:
        """
        Call Groq LLM API for text generation
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            Generated text response
        """
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return "Error: GROQ_API_KEY environment variable not set"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            return f"Error calling Groq API: {str(e)}"
    
    def _assess_medical_risk(self, question: str, answer: str, context: str) -> Dict[str, str]:
        """
        Assess medical risk level based on question and answer
        
        Args:
            question: User's question
            answer: Generated answer
            context: Retrieved context
            
        Returns:
            dict with risk_level and risk_reason
        """
        # Risk keywords detection
        high_risk_keywords = [
            "emergency", "urgent", "severe", "critical", "chest pain", "stroke", 
            "heart attack", "bleeding", "unconscious", "breathing difficulty",
            "suicide", "overdose", "trauma", "acute", "life-threatening"
        ]
        
        medium_risk_keywords = [
            "pain", "fever", "infection", "injury", "symptoms", "treatment",
            "medication", "diagnosis", "chronic", "persistent", "abnormal"
        ]
        
        # Check question and answer content
        combined_text = (question + " " + answer + " " + context).lower()
        
        for keyword in high_risk_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "HIGH",
                    "risk_reason": f"Detected urgent medical keywords: '{keyword}'. Immediate medical attention may be required."
                }
        
        for keyword in medium_risk_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "MEDIUM",
                    "risk_reason": f"Medical attention may be needed. Consider consulting a healthcare professional."
                }
        
        return {
            "risk_level": "LOW",
            "risk_reason": "General medical information query. No immediate concerns detected."
        }
    
    def answer_question(self, question: str, context_docs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Answer a question using RAG with Groq LLM
        
        Args:
            question: User's question
            context_docs: Optional list of context documents (if None, retrieves from vector store)
            
        Returns:
            dict with:
                - answer: Generated answer text
                - risk_level: Risk assessment (LOW/MEDIUM/HIGH)
                - risk_reason: Explanation of risk level
                - source_documents: List of source document snippets
        """
        try:
            # Retrieve relevant documents if not provided
            if context_docs is None:
                if self.retriever is None:
                    return {
                        "answer": "Error: Vector store not initialized",
                        "risk_level": "UNKNOWN",
                        "risk_reason": "System error",
                        "source_documents": []
                    }
                
                relevant_docs = self.retriever.get_relevant_documents(question)
                source_documents = [doc.page_content for doc in relevant_docs]
                context = "\n\n".join(source_documents[:3])
            else:
                source_documents = context_docs
                context = "\n\n".join(context_docs[:3])
            
            # Build chat history context
            history_context = ""
            if self.chat_history:
                history_context = "\n".join([
                    f"User: {h['question']}\nAssistant: {h['answer']}"
                    for h in self.chat_history[-2:]  # Last 2 exchanges
                ])
                history_context = f"\n\nPrevious conversation:\n{history_context}\n\n"
            
            # Create prompt for Groq
            prompt = f"""You are a helpful medical assistant for a hospital system. Use the following context to answer the question accurately and professionally.

IMPORTANT:
- Provide clear, evidence-based medical information
- If the answer is not in the context, state that clearly
- For urgent symptoms, recommend immediate medical attention
- Always encourage consulting healthcare professionals for diagnosis

{history_context}Context from medical documents:
{context}

Question: {question}

Answer:"""
            
            # Call Groq API
            answer = self._call_groq(prompt)
            
            # Assess medical risk
            risk_assessment = self._assess_medical_risk(question, answer, context)
            
            # Update chat history
            self.chat_history.append({"question": question, "answer": answer})
            if len(self.chat_history) > 4:  # Keep last 4 exchanges
                self.chat_history.pop(0)
            
            return {
                "answer": answer,
                "risk_level": risk_assessment["risk_level"],
                "risk_reason": risk_assessment["risk_reason"],
                "source_documents": source_documents
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "risk_level": "UNKNOWN",
                "risk_reason": "System error occurred",
                "source_documents": []
            }
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get chat history"""
        return self.chat_history.copy()


# Standalone function for simple usage
def answer_question(question: str, vector_store_name: str = "DefaultVectorDB", 
                   context_docs: Optional[List[str]] = None,
                   max_tokens: int = 500) -> Dict[str, Any]:
    """
    Standalone function to answer a question using RAG
    
    Args:
        question: User's question
        vector_store_name: Name of the vector store to use
        context_docs: Optional list of context documents
        max_tokens: Maximum tokens for response
        
    Returns:
        dict with answer, risk_level, risk_reason, source_documents
    """
    engine = RAGEngine(vector_store_name=vector_store_name, max_tokens=max_tokens)
    return engine.answer_question(question, context_docs)
