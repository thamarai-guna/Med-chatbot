"""
RAG Engine - Core logic for medical chatbot
Streamlit-independent module for RAG-based question answering with Groq LLM API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from patient_manager import get_patient_manager

load_dotenv()


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for medical Q&A with dual vector store support
    Retrieves from BOTH shared medical books AND patient-specific medical records
    """
    
    def __init__(self, patient_id: str, max_tokens: int = 500, temperature: float = 0.7):
        """
        Initialize RAG engine with dual vector store retrieval
        
        Args:
            patient_id: Unique patient identifier (MANDATORY)
            max_tokens: Maximum tokens for LLM response
            temperature: LLM temperature (0.0-1.0)
        """
        if not patient_id:
            raise ValueError("patient_id is mandatory and cannot be empty")
        
        self.patient_id = patient_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.chat_history = []
        self.shared_retriever = None
        self.patient_retriever = None
        self.patient_manager = get_patient_manager()
        
        # Verify patient exists
        patient = self.patient_manager.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found. Please register first.")
        
        # Load patient's chat history
        self._load_patient_history()
        
        # Load dual vector stores (shared medical books + patient records)
        self._load_dual_vector_stores()
    
    def _load_patient_history(self):
        """Load patient's previous chat history from database"""
        try:
            history = self.patient_manager.get_patient_history(self.patient_id, limit=50)
            # Convert to expected format
            self.chat_history = [
                {
                    "question": h["question"],
                    "answer": h["answer"],
                    "risk_level": h["risk_level"],
                    "risk_reason": h["risk_reason"],
                    "timestamp": h["timestamp"]
                }
                for h in history
            ]
        except Exception as e:
            print(f"Warning: Could not load patient history: {e}")
            self.chat_history = []
    
    def _load_dual_vector_stores(self):
        """
        Load TWO vector stores:
        1. Shared medical books (system-wide, read-only)
        2. Patient-specific medical records (private, per-patient)
        """
        try:
            instructor_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2", 
                model_kwargs={'device': 'cpu'}
            )
            
            # Load shared medical books vector store (ALWAYS AVAILABLE)
            shared_path = "vector store/shared"
            if os.path.exists(shared_path):
                shared_db = FAISS.load_local(
                    shared_path,
                    instructor_embeddings,
                    allow_dangerous_deserialization=True
                )
                self.shared_retriever = shared_db.as_retriever(search_kwargs={"k": 3})
                print(f"✅ Loaded shared medical books vector store")
            else:
                print(f"⚠️ Shared medical books vector store not found at {shared_path}")
                self.shared_retriever = None
            
            # Load patient-specific vector store (IF EXISTS)
            patient_path = f"vector store/patient_{self.patient_id}"
            if os.path.exists(patient_path):
                patient_db = FAISS.load_local(
                    patient_path,
                    instructor_embeddings,
                    allow_dangerous_deserialization=True
                )
                self.patient_retriever = patient_db.as_retriever(search_kwargs={"k": 3})
                print(f"✅ Loaded patient-specific medical records for {self.patient_id}")
            else:
                print(f"ℹ️ No patient-specific medical records found for {self.patient_id}")
                self.patient_retriever = None
            
            # At least one retriever must be available
            if not self.shared_retriever and not self.patient_retriever:
                raise RuntimeError("No vector stores available. System medical books not loaded.")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load vector stores: {str(e)}")
    
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
            "model": "llama-3.3-70b-versatile",
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
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.HTTPError as e:
            # Try to extract error details from response
            try:
                error_detail = e.response.json() if hasattr(e.response, 'json') else str(e.response.text)
                return f"Error calling Groq API: {e.response.status_code} - {str(error_detail)}"
            except:
                return f"Error calling Groq API: {str(e)}"
        except requests.exceptions.RequestException as e:
            return f"Error calling Groq API: {str(e)}"
    
    def _assess_medical_risk(self, question: str, answer: str, context: str) -> Dict[str, str]:
        """
        Assess medical risk level using LLM reasoning
        
        Args:
            question: User's question
            answer: Generated answer
            context: Retrieved context
            
        Returns:
            dict with risk_level and risk_reason
        """
        # Build chat history context for risk assessment
        history_summary = ""
        if self.chat_history:
            recent_exchanges = self.chat_history[-3:]  # Last 3 exchanges
            history_summary = "\n".join([
                f"Previous Q: {h['question']}\nPrevious A: {h['answer'][:200]}"
                for h in recent_exchanges
            ])
        
        # Create risk assessment prompt
        risk_prompt = self._create_risk_assessment_prompt(
            question=question,
            answer=answer,
            context=context,
            history=history_summary
        )
        
        try:
            # Call Groq API for risk assessment
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return {
                    "risk_level": "UNKNOWN",
                    "risk_reason": "API key not configured"
                }
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_risk_assessment_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": risk_prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.3,  # Lower temperature for more consistent risk assessment
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            risk_json = data["choices"][0]["message"]["content"].strip()
            
            # Parse JSON response
            import json
            risk_data = json.loads(risk_json)
            
            # Normalize risk_level to uppercase
            risk_level = risk_data.get("risk_level", "UNKNOWN").upper()
            risk_reason = risk_data.get("risk_reason", "Unable to assess risk")
            
            return {
                "risk_level": risk_level,
                "risk_reason": risk_reason
            }
            
        except Exception as e:
            # Fallback to basic keyword detection if LLM fails
            return self._fallback_risk_assessment(question, answer, context)
    
    def _get_risk_assessment_system_prompt(self) -> str:
        """
        System prompt for risk assessment
        """
        return """You are a medical risk assessment AI for a hospital triage system. Your task is to evaluate medical queries and assign a risk level.

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

IMPORTANT: Consider the conversation history for progression of symptoms. If symptoms are recurring or worsening across multiple questions, this indicates higher risk."""

    def _create_risk_assessment_prompt(self, question: str, answer: str, context: str, history: str) -> str:
        """
        User prompt for risk assessment with all context
        """
        prompt = f"""Assess the medical risk level for this patient interaction.

PATIENT QUESTION:
{question}

MEDICAL ANSWER PROVIDED:
{answer}

RELEVANT MEDICAL CONTEXT FROM DOCUMENTS:
{context[:800]}"""

        if history:
            prompt += f"""

CONVERSATION HISTORY (for symptom progression analysis):
{history}"""

        prompt += """

Analyze the above information and respond with JSON only:
{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_reason": "Brief explanation (1-2 sentences max)"
}"""

        return prompt
    
    def _fallback_risk_assessment(self, question: str, answer: str, context: str) -> Dict[str, str]:
        """
        Fallback keyword-based risk assessment if LLM fails
        """
        combined_text = (question + " " + answer + " " + context).lower()
        
        critical_keywords = [
            "cardiac arrest", "not breathing", "unconscious", "unresponsive",
            "severe bleeding", "major trauma", "stroke symptoms"
        ]
        
        high_risk_keywords = [
            "chest pain", "stroke", "heart attack", "severe", "breathing difficulty",
            "confusion", "vision loss", "numbness", "weakness", "suicide"
        ]
        
        medium_risk_keywords = [
            "pain", "fever", "infection", "persistent", "worsening", "chronic"
        ]
        
        for keyword in critical_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "CRITICAL",
                    "risk_reason": f"Life-threatening condition detected. Immediate medical attention required."
                }
        
        for keyword in high_risk_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "HIGH",
                    "risk_reason": f"Urgent medical attention may be needed within hours."
                }
        
        for keyword in medium_risk_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "MEDIUM",
                    "risk_reason": "Medical evaluation recommended soon."
                }
        
        return {
            "risk_level": "LOW",
            "risk_reason": "General medical information query with no immediate concerns."
        }
    
    def answer_question(self, question: str, context_docs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Answer a question using dual RAG retrieval with Groq LLM
        Retrieves context from BOTH shared medical books AND patient records
        
        Args:
            question: User's question
            context_docs: Optional list of context documents (if None, retrieves from both vector stores)
            
        Returns:
            dict with:
                - answer: Generated answer text
                - risk_level: Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
                - risk_reason: Explanation of risk level
                - source_documents: List of source document snippets
        """
        try:
            # Retrieve relevant documents from BOTH stores if not provided
            if context_docs is None:
                source_documents = []
                
                # Retrieve from shared medical books
                if self.shared_retriever:
                    shared_docs = self.shared_retriever.invoke(question)
                    source_documents.extend([doc.page_content for doc in shared_docs])
                
                # Retrieve from patient-specific records
                if self.patient_retriever:
                    patient_docs = self.patient_retriever.invoke(question)
                    source_documents.extend([doc.page_content for doc in patient_docs])
                
                # If no retrievers available, return error
                if not source_documents:
                    return {
                        "answer": "Error: No medical knowledge sources available",
                        "risk_level": "UNKNOWN",
                        "risk_reason": "System error",
                        "source_documents": []
                    }
                
                # Combine contexts (prioritize patient records, then medical books)
                context = "\n\n".join(source_documents[:6])  # Top 6 chunks total
            else:
                source_documents = context_docs
                context = "\n\n".join(context_docs[:6])
            
            # Build chat history context
            history_context = ""
            if self.chat_history:
                history_context = "\n".join([
                    f"User: {h['question']}\nAssistant: {h['answer']}"
                    for h in self.chat_history[-2:]  # Last 2 exchanges
                ])
                history_context = f"\n\nPrevious conversation:\n{history_context}\n\n"
            
            # Create prompt for Groq with combined context
            prompt = f"""You are an AI chatbot designed to monitor patients with brain-related conditions after hospital discharge.

CONTEXT:
- Brain-related medical books and guidelines have already been uploaded.
- These documents are stored in a vector database.
- You must use Retrieval-Augmented Generation (RAG) to retrieve information from these books whenever medical reasoning is required.
- Do not use any medical knowledge outside the retrieved content.

PATIENT DATA:
- Patient medical reports will be provided after the books are uploaded.
- Use the patient reports only to understand the condition, symptoms, medications, and risk factors.
- Do not treat patient reports as medical knowledge.

YOUR TASK:
- Ask simple and clear questions to the patient based on their reports.
- Use only simple language and ask ONE question at a time.
- Prefer Yes/No or short answers.
- Adapt follow-up questions based on patient responses.
- Focus only on brain-related symptoms.

CRITICAL INSTRUCTION: 
🚨 ASK ONLY **ONE QUESTION** PER RESPONSE 🚨
- Do NOT list multiple questions
- Do NOT ask "question 1, question 2, question 3"
- Ask one question, wait for the patient's answer, then ask the next question in the next interaction

QUESTION AREAS:
- Speech or confusion
- Headache or pain
- Dizziness or balance
- Weakness or numbness
- Vision problems
- Seizure activity (if mentioned)
- Medication intake
- Daily functioning

ASSESSMENT:
- Combine patient responses, patient reports, and retrieved medical guidance.
- Analyze symptom severity, duration, and combinations.
- Classify the patient into one risk level: Low, Medium, or High.

FINAL RESPONSE FORMAT (AFTER GATHERING INFORMATION):

1. Risk Level:
   - Low / Medium / High

2. Reason:
   - Explain the risk level using simple bullet points.
   - Base the explanation on patient responses and retrieved guidance.

3. Actions (STRICT RULES):

   - If Risk Level is HIGH:
     Tell the patient to visit their doctor or the nearest hospital immediately.
     Encourage contacting a caregiver or family member.
     Do NOT give medication advice.

   - If Risk Level is MEDIUM:
     Advise the patient to continue taking the medicines prescribed by the doctor.
     Reinforce following the doctor's instructions.
     Encourage rest and monitoring.
     Do NOT suggest new medicines or dosage changes.

   - If Risk Level is LOW:
     Reassure the patient using positive and calming words.
     Tell the patient they are doing well and should not worry.
     Encourage continuing normal routine and prescribed medication.

SAFETY RULES:
- Do not diagnose diseases.
- Do not change or prescribe medicines.
- Do not replace a doctor.
- Always prioritize patient safety.

TONE:
- Calm
- Supportive
- Clear
- Patient-friendly

{history_context}Context from medical sources (books + patient records):
{context}

Patient's current message: {question}

Your response (remember: ask ONE question only, or provide assessment if enough information gathered):"""
            
            # Call Groq API
            answer = self._call_groq(prompt)
            
            # Assess medical risk
            risk_assessment = self._assess_medical_risk(question, answer, context)
            
            # Update chat history
            self.chat_history.append({"question": question, "answer": answer})
            if len(self.chat_history) > 4:  # Keep last 4 exchanges
                self.chat_history.pop(0)
            
            # Save to patient database
            self.patient_manager.save_chat_message(
                patient_id=self.patient_id,
                question=question,
                answer=answer,
                risk_level=risk_assessment["risk_level"],
                risk_reason=risk_assessment["risk_reason"],
                source_documents=source_documents
            )
            
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


# Standalone function for simple usage (DEPRECATED - use class directly)
def answer_question(question: str, patient_id: str, context_docs: Optional[List[str]] = None,
                   max_tokens: int = 500) -> Dict[str, Any]:
    """
    Standalone function to answer a question using dual RAG
    
    DEPRECATED: Use RAGEngine class directly for better control
    
    Args:
        question: User's question
        patient_id: Patient identifier (MANDATORY)
        context_docs: Optional list of context documents
        max_tokens: Maximum tokens for response
        
    Returns:
        dict with answer, risk_level, risk_reason, source_documents
    """
    if not patient_id:
        raise ValueError("patient_id is required")
    
    engine = RAGEngine(patient_id=patient_id, max_tokens=max_tokens)
    return engine.answer_question(question, context_docs)
