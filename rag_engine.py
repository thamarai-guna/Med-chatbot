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
        self.question_count = 0  # Track questions in current session
        self.max_questions_per_session = 6  # Enforce maximum (per latest spec)
        
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
            reason = risk_data.get("reason", ["Unable to assess"])
            action = risk_data.get("action", "Continue monitoring")
            
            return {
                "risk_level": risk_level,
                "reason": reason if isinstance(reason, list) else [reason],
                "action": action
            }
            
        except Exception as e:
            # Fallback to basic keyword detection if LLM fails
            return self._fallback_risk_assessment(question, answer, context)
    
    def _get_risk_assessment_system_prompt(self) -> str:
        """
        System prompt for neurological risk assessment (post-discharge monitoring)
        """
        return """You are a post-discharge neurological monitoring assistant. Your task is to assess patient risk based on symptom responses.

CRITICAL RULES:
1. You MUST respond with VALID JSON ONLY (no other text before or after)
2. JSON format: {"risk_level": "LOW|MEDIUM|HIGH", "reason": ["bullet1", "bullet2"], "action": "action text"}
3. risk_level: ONLY ONE of LOW, MEDIUM, HIGH (be CONSERVATIVE)
4. reason: Array of 1-3 bullet points maximum, simple language, NO diagnosis, NO medical jargon
5. action: Plain text action based on risk level

RISK LEVEL DEFINITIONS (NEUROLOGICAL FOCUS):
- HIGH: Neurological red flags (confusion, severe headache, sudden weakness, loss of sensation, vision loss, seizure activity, speech difficulties, severe dizziness, worsening symptoms)
- MEDIUM: Moderate symptoms (persistent headache, mild dizziness, mild numbness, medication questions, functional limitations)
- LOW: Stable symptoms, no new concerns, following treatment plan, doing well

Be CONSERVATIVE: Only use HIGH if symptoms clearly justify urgent attention.

ACTION RULES (STRICT):
- HIGH: "Visit your doctor or nearest hospital immediately. Contact a family member or caregiver."
- MEDIUM: "Continue taking your prescribed medicines and monitor symptoms closely. Inform your doctor if symptoms worsen."
- LOW: "You are doing well. Continue your normal routine and prescribed medications. No immediate action needed."

IMPORTANT: Consider conversation history for symptom progression. Worsening trends increase risk level."""

    def _create_risk_assessment_prompt(self, question: str, answer: str, context: str, history: str) -> str:
        """
        User prompt for neurological risk assessment with all context
        """
        prompt = f"""Assess the neurological risk level for this patient post-discharge monitoring session.

PATIENT'S SYMPTOM RESPONSE:
{question}

PATIENT'S ANSWER/SYMPTOMS:
{answer}

RELEVANT MEDICAL CONTEXT FROM NEUROLOGY DOCUMENTS:
{context[:800]}"""

        if history:
            prompt += f"""

CONVERSATION HISTORY (check for symptom progression):
{history}"""

        prompt += """

Analyze and respond with VALID JSON ONLY (no other text):
{
  "risk_level": "LOW|MEDIUM|HIGH",
  "reason": ["symptom description", "severity assessment", "trend if worsening"],
  "action": "specific action for patient"
}

Remember: Be CONSERVATIVE. Use HIGH only if clearly justified."""

        return prompt
    
    def _fallback_risk_assessment(self, question: str, answer: str, context: str) -> Dict[str, str]:
        """
        Fallback keyword-based risk assessment if LLM fails (neurological focus)
        """
        combined_text = (question + " " + answer + " " + context).lower()
        
        high_risk_keywords = [
            "seizure", "confusion", "lost consciousness", "sudden weakness",
            "vision loss", "numbness", "severe headache", "speech difficulty",
            "severe dizziness", "can't walk", "paralysis", "stroke", "bleeding"
        ]
        
        medium_risk_keywords = [
            "headache", "mild dizziness", "numbness", "weakness",
            "persistent", "worsening", "medication", "dizzy"
        ]
        
        for keyword in high_risk_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "HIGH",
                    "reason": ["Neurological symptoms detected", "Requires urgent medical attention"],
                    "action": "Visit your doctor or nearest hospital immediately. Contact a family member or caregiver."
                }
        
        for keyword in medium_risk_keywords:
            if keyword in combined_text:
                return {
                    "risk_level": "MEDIUM",
                    "reason": ["Moderate neurological symptoms present", "Monitoring recommended"],
                    "action": "Continue taking your prescribed medicines and monitor symptoms closely. Inform your doctor if symptoms worsen."
                }
        
        return {
            "risk_level": "LOW",
            "reason": ["Stable condition", "No acute symptoms reported"],
            "action": "You are doing well. Continue your normal routine and prescribed medications."
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
            
            # Pre-upload guard: if no patient-specific vector store, require upload
            if self.patient_retriever is None:
                upload_msg = "To begin today’s check-in, please upload your medical reports using the **Upload Medical Reports** section above."
                return {
                    "answer": upload_msg,
                    "risk_level": "PENDING",
                    "risk_reason": upload_msg,
                    "reason": [upload_msg],
                    "action": upload_msg,
                    "source_documents": [],
                    "question_count": self.question_count
                }

            # Build chat history context
            history_context = ""
            if self.chat_history:
                history_context = "\n".join([
                    f"User: {h['question']}\nAssistant: {h['answer']}"
                    for h in self.chat_history[-2:]  # Last 2 exchanges
                ])
                history_context = f"\n\nPrevious conversation:\n{history_context}\n\n"
            
            # Create prompt for Groq with combined context
            prompt = f"""You are an AI assistant for post-discharge neurological patient monitoring.

You are NOT a general chatbot. You operate ONLY within a controlled hospital monitoring flow.

MANDATORY FLOW (STRICT):
1) User login (already completed)
2) Patient identity established
3) Patient medical reports uploaded
4) Report processing completed
5) Questioning begins
6) Risk assessment generated

PRE-CONDITION:
- If patient medical reports are NOT uploaded or processed, do NOT ask questions. Instead say: "Please upload your medical reports to continue with today’s check-in."

DOCUMENT SOURCES:
- SOURCE A (Shared books): Neurology clinical books/guidelines in vector DB. Use ONLY for medical reasoning via RAG.
- SOURCE B (Patient reports): Private PDFs/images/text for condition/symptoms/meds/risk factors. NOT medical knowledge; do NOT use for medical reasoning.

YOUR ROLE:
1) Ask DAILY symptom questions after reports are uploaded
2) Adapt questions using patient report context + previous answers + retrieved guidance
3) Assess patient risk (LOW/MEDIUM/HIGH)
4) Provide safe next-step actions

QUESTION RULES (STRICT):
- Ask ONE question at a time (exactly one line)
- Simple, patient-friendly language
- Focus ONLY on brain-related symptoms
- Areas: Speech/confusion, Headache/pain, Dizziness/balance, Weakness/numbness, Vision, Seizures (if mentioned), Medications, Daily functioning
- Allowed answer types: YES/NO OR numeric (0-10) OR short text (10-15 words; only for pain location or new symptoms)
- Question number: {self.question_count + 1}/{self.max_questions_per_session}
- Limits: MIN 3, MAX 6 questions. Never exceed max. End early if stable.

FOLLOW-UP RULES:
- Only if patient answers YES or symptom worsens
- Only ONE follow-up per symptom
- Follow-ups obey all rules above

ASSESSMENT LOGIC:
- Combine: patient answers + patient report context + retrieved neurology guidance
- Analyze severity, trends, combinations

FINAL RESPONSE FORMAT (STRICT JSON when ready):
{{
    "risk_level": "LOW|MEDIUM|HIGH",
    "reason": ["bullet1", "bullet2"],
    "action": "specific action text"
}}

REASON RULES:
- 1-3 bullets, simple language, no diagnosis, no jargon, no sources

ACTION RULES (STRICT):
- HIGH: Visit doctor/hospital immediately; contact caregiver. No medication advice.
- MEDIUM: Continue prescribed medicines; rest and monitor; no new meds or dosage changes.
- LOW: Reassure; continue normal routine and prescribed meds.

SAFETY RULES:
- Do NOT diagnose; do NOT prescribe/change meds; do NOT replace a doctor; prioritize safety

TONE: Calm, Supportive, Clear, Patient-friendly

Retrieved medical context:
{context[:1000]}

{history_context}

Now ask the next symptom question (ONE line, ONE allowed answer type). If reports are missing, say: "Please upload your medical reports to continue with today’s check-in." If you have enough info (≥3 questions or at max limit), return the JSON assessment instead of another question."""
            
            # Call Groq API
            answer = self._call_groq(prompt)
            
            # Increment question counter
            self.question_count += 1
            
            # Try to parse JSON if assessment is complete
            risk_assessment = None
            try:
                # Check if answer contains JSON (assessment format)
                if "risk_level" in answer.lower():
                    import json
                    # Extract JSON from response
                    json_start = answer.find('{')
                    json_end = answer.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_str = answer[json_start:json_end]
                        risk_data = json.loads(json_str)
                        risk_assessment = {
                            "risk_level": risk_data.get("risk_level", "UNKNOWN").upper(),
                            "reason": risk_data.get("reason", ["Unable to assess"]),
                            "action": risk_data.get("action", "Continue monitoring")
                        }
                        # Reset question counter for next session
                        self.question_count = 0
            except:
                pass
            
            # If no assessment yet, assess based on conversation depth
            if not risk_assessment and self.question_count >= self.max_questions_per_session:
                # Force assessment at max questions (6)
                risk_assessment = self._assess_medical_risk(question, answer, context)
            elif not risk_assessment and self.question_count >= 3:
                # Minimum questions reached (3)
                risk_assessment = self._assess_medical_risk(question, answer, context)
            elif not risk_assessment:
                # Still asking questions
                risk_assessment = {
                    "risk_level": "PENDING",
                    "reason": ["Gathering symptom information"],
                    "action": answer  # Return the question
                }
            
            # Save to patient database
            risk_level = risk_assessment.get("risk_level", "UNKNOWN")
            # Convert reason array to string for database storage
            reason_list = risk_assessment.get("reason", [])
            if isinstance(reason_list, list) and reason_list:
                risk_reason = reason_list[0]  # Use first bullet point
            else:
                risk_reason = str(risk_assessment.get("action", ""))

            # Enforce pre-condition: if no patient records, return upload message and skip logging
            if self.patient_retriever is None:
                upload_msg = "Please upload your medical reports to continue with today’s check-in."
                return {
                    "answer": upload_msg,
                    "risk_level": "PENDING",
                    "risk_reason": upload_msg,
                    "reason": [upload_msg],
                    "action": upload_msg,
                    "source_documents": [],
                    "question_count": self.question_count
                }

            self.patient_manager.save_chat_message(
                patient_id=self.patient_id,
                question=question,
                answer=answer,
                risk_level=risk_level,
                risk_reason=risk_reason,
                source_documents=source_documents
            )
            
            return {
                "answer": answer,
                "risk_level": risk_level,
                "risk_reason": risk_reason,  # Convert back to string for API compatibility
                "reason": risk_assessment.get("reason", []),  # Include array for reference
                "action": risk_assessment.get("action", ""),
                "source_documents": source_documents,
                "question_count": self.question_count
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
