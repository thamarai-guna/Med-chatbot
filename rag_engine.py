"""
RAG Engine - Core logic for medical chatbot
Streamlit-independent module for RAG-based question answering with Groq LLM API
"""



import os
import json
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from patient_manager import get_patient_manager

load_dotenv()

import contextlib
@contextlib.contextmanager
def silence_output():
    """Context manager to suppress stdout and stderr to prevent UnicodeEncodeError on Windows"""
    with open(os.devnull, "w", encoding='utf-8') as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            yield


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
        self.max_questions_per_session = 5  # Enforce maximum (user requested 5)
        
        # --- Configure Multi-Provider Fallback ---
        
        # 1. DeepSeek (Primary)
        self.deepseek_client = None
        ds_key = os.getenv("DEEPSEEK_API_KEY")
        if ds_key:
            self.deepseek_client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com")
        
        # 2. Groq (Secondary)
        self.groq_client = None
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.groq_client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            
        # 3. Gemini (Tertiary)
        self.gemini_model = None
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
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
            
            # Restore question count for TODAY's session
            # We count how many questions the assistant has already asked today
            today = datetime.utcnow().date()
            self.question_count = 0
            
            for h in self.chat_history:
                try:
                    # Parse timestamp (SQLite default is "YYYY-MM-DD HH:MM:SS" which might not start with 'T')
                    ts_str = h["timestamp"]
                    if 'T' in ts_str:
                        msg_time = datetime.fromisoformat(ts_str).date()
                    else:
                        # Handle SQLite default format "YYYY-MM-DD HH:MM:SS"
                        msg_time = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").date()
                    
                    if msg_time == today:
                        # Assuming each history entry represents one Q&A pair (one question asked)
                        self.question_count += 1
                except Exception as e:
                    print(f"Error parsing timestamp {h.get('timestamp')}: {e}")
                    pass
            
            print(f"[RAG] Patient {self.patient_id} History Length: {len(self.chat_history)}")     
            print(f"[RAG] Restored question count from history: {self.question_count}")
            print(f"[RAG] Today is: {today}")
            
        except Exception as e:
            print(f"Warning: Could not load patient history: {e}")
            self.chat_history = []
            self.question_count = 0
    
    def _strip_acknowledgement(self, text: str) -> str:
        """Helper to remove the standard acknowledgment boilerplate from text using Regex"""
        import re
        # Pattern matches "Thank you... check-in." or similar variations
        pattern = r"^(Thank you.*?check-in\.|Thank you.*?report\.)\s*"
        return re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL).strip()




    


    def _load_dual_vector_stores(self):
        """
        Load TWO vector stores:
        1. Shared medical books (system-wide, read-only)
        2. Patient-specific medical records (private, per-patient)
        """
        try:
            with silence_output():
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
                else:
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
                else:
                    self.patient_retriever = None
            
            # Print status safely (outside silenced block)
            if self.shared_retriever:
                print(f"[INFO] Loaded shared medical books")
            else:
                print(f"[WARN] Shared vector store not found")
                
            if self.patient_retriever:
                print(f"[INFO] Loaded patient records for {self.patient_id}")
            else:
                print(f"[INFO] No patient records for {self.patient_id}")
            
            # At least one retriever must be available
            if not self.shared_retriever and not self.patient_retriever:
                raise RuntimeError("No vector stores available. System medical books not loaded.")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load vector stores: {str(e)}")
    
    def _call_llm_with_fallback(self, prompt: str) -> str:
        """
        Try LLM providers in order: DeepSeek -> Groq -> Gemini
        """
        errors = []
        
        # 1. Try DeepSeek (Primary)
        if self.deepseek_client:
            try:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                errors.append(f"DeepSeek Error: {e}")
                print(f"[WARN] DeepSeek failed: {e}. Trying Groq...")

        # 2. Try Groq (Secondary)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                errors.append(f"Groq Error: {e}")
                print(f"[WARN] Groq failed: {e}. Trying Gemini...")

        # 3. Try Gemini (Tertiary)
        if self.gemini_model:
            try:
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                response = self.gemini_model.generate_content(prompt, generation_config=generation_config)
                return response.text.strip()
            except Exception as e:
                errors.append(f"Gemini Error: {e}")
                print(f"[WARN] Gemini failed: {e}.")

        return f"Error: All LLM providers failed. Details: {'; '.join(errors)}"

    def _call_llm_with_fallback_stream(self, prompt: str):
        """
        Stream from LLM providers in order: DeepSeek -> Groq -> Gemini
        Yields chunk text
        """
        # 1. Try DeepSeek (Primary)
        if self.deepseek_client:
            try:
                # We only try to initialize stream. If it works, we assume connection is good.
                stream = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return # Success, stop
            except Exception as e:
                print(f"[WARN] DeepSeek stream failed: {e}. Trying Groq...")
        
        # 2. Try Groq (Secondary)
        if self.groq_client:
            try:
                stream = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return # Success
            except Exception as e:
                print(f"[WARN] Groq stream failed: {e}. Trying Gemini...")

        # 3. Try Gemini (Tertiary)
        if self.gemini_model:
            try:
                # Gemini streaming is slightly different
                response = self.gemini_model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                print(f"[WARN] Gemini stream failed: {e}.")

        yield "Error: All LLM providers failed to stream."

    def answer_question_stream(self, question: str, context_docs: Optional[List[str]] = None):
        """
        Generator yielding chunks of the answer.
        Buffers full answer to process risk assessment at the end.
        """
        # 1. Retrieve & Prepare Context (BLOCKING)
        if context_docs is None:
            source_documents = []
            if self.shared_retriever:
                shared_docs = self.shared_retriever.invoke(question)
                source_documents.extend([doc.page_content for doc in shared_docs])
            if self.patient_retriever:
                patient_docs = self.patient_retriever.invoke(question)
                source_documents.extend([doc.page_content for doc in patient_docs])
            
            if not source_documents:
                yield "Error: No medical knowledge sources available"
                return

            context = "\n\n".join(source_documents[:6])
        else:
            source_documents = context_docs
            context = "\n\n".join(context_docs[:6])

        # Pre-upload check (Blocking first chunk)
        if self.patient_retriever is None:
            yield "To begin today’s check-in, please upload your medical reports using the **Upload Medical Reports** section above."
            return

        # Build prompt
        history_context = ""
        if self.chat_history:
            history_context = "\n".join([
                f"User: {h['question']}\nAssistant: {self._strip_acknowledgement(h['answer'])}"
                for h in self.chat_history[-3:]
            ])
            history_context = f"\n\nPrevious conversation:\n{history_context}\n\n"

        prompt = f"""You are a specialized Neurological Medical Assistant designed for post-discharge patient monitoring.

Your task is to assess the patient's neurological health status based on a short interaction.

RULES:
1. Ask a maximum of {self.max_questions_per_session} simple, yes/no or scale-based questions.
2. Questions must be short, clear, and STRICTLY RELATED to the patient's neurological condition (e.g., headache, vision, balance, confusion, weakness, numbness).
3. If the user reports general symptoms (fever, cough, etc.), acknowledge them but IMMEDIATELY ask if they are experiencing any associated neurological symptoms (e.g., "Do you have a stiff neck or headache with that fever?").
4. NOT ask follow-up questions beyond the limit.
5. After collecting answers, produce the final assessment in the specified format.
6. Do NOT include explanations outside the format.
7. Do NOT provide medical diagnosis—only risk assessment and guidance.

CONTEXT:
Current Question Number: {self.question_count + 1}/{self.max_questions_per_session}

MANDATORY SYSTEM RULES (Hidden):
- If {self.question_count + 1} <= {self.max_questions_per_session}: Ask the next question.
- If {self.question_count + 1} > {self.max_questions_per_session}: Stop asking and provide the FINAL OUTPUT.

FINAL OUTPUT FORMAT (User Visible):

Risk Level: <Low / Medium / High>

Action:
- <Clear next step the patient should take>

Reason:
- <Brief justification based on the patient's responses, emphasizing neurological context>


IMPORTANT FOR SYSTEM INTEGRATION (Backend Only):
Regardless of the user-visible output, when you produce the final assessment, you MUST ALSO append a JSON block at the very end of your response (it will be hidden from the user).
Format:
{{
    "risk_level": "LOW|MEDIUM|HIGH",
    "reason": ["reason 1"],
    "action": "action text"
}}

Retrieved medical context (Prioritize NEUROLOGICAL info):
{context[:1000]}

{history_context}

Start directly with the NEXT question. If you have enough info (>=3 questions or at max limit), return the FINAL OUTPUT (Text + JSON)."""

        full_answer_buffer = ""

        # 2. Stream Response
        stream_gen = self._call_llm_with_fallback_stream(prompt)
        
        # Ack check for first chunk
        first_chunk = True
        
        for chunk in stream_gen:
            # Special First Chunk Handling for Acknowledgment
            if first_chunk and self.question_count == 0:
                 # We can't easily check for assessment in first chunk, so we just prepend acknowledgment if consistent with logic
                 # But streaming makes prepending weird visually if acknowledgement comes later.
                 # Strategy: Just yield chunk. We'll rely on frontend or just assume streaming works.
                 # Actually, let's prepend the Ack to the first chunk if rules match
                 if self.patient_retriever is not None:
                     # Check if we should ack? Hard to know if response contains assessment yet.
                     # Let's emit Ack first as a separate event/chunk
                     yield "Thank you. I’ve reviewed your medical report. Let’s begin today’s check-in.\n\n"
                     full_answer_buffer += "Thank you. I’ve reviewed your medical report. Let’s begin today’s check-in.\n\n"
                     first_chunk = False
            
            full_answer_buffer += chunk
            yield chunk

        # 3. Post-Processing (Background logic after stream ends)
        # We need to save state.
        # But we are inside a generator. The generator finishes when this loop ends.
        # So we can do post-processing here!
        
        self.question_count += 1
        
        risk_assessment = None
        risk_level = "UNKNOWN"
        risk_reason = ""
        action_text = ""
        
        # Parse JSON from full buffer
        import json
        lower_answer = full_answer_buffer.lower()
        if "risk_level" in lower_answer:
            json_start = full_answer_buffer.find('{')
            json_end = full_answer_buffer.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                try:
                    json_str = full_answer_buffer[json_start:json_end]
                    risk_data = json.loads(json_str)
                    risk_assessment = {
                        "risk_level": risk_data.get("risk_level", "UNKNOWN").upper(),
                        "reason": risk_data.get("reason", ["Unable to assess"]),
                        "action": risk_data.get("action", "Continue monitoring")
                    }
                    risk_level = risk_assessment["risk_level"]
                    action_text = risk_assessment["action"]
                    
                    reason_list = risk_assessment["reason"]
                    if isinstance(reason_list, list) and reason_list:
                         risk_reason = reason_list[0]
                    else:
                         risk_reason = str(risk_assessment.get("action",""))
                         
                except:
                    pass

        # Save to DB
        self.patient_manager.save_chat_message(
            patient_id=self.patient_id,
            question=question,
            answer=full_answer_buffer, # Note: This includes the hidden JSON. Ideally we strip it before saving or save clean version.
            risk_level=risk_level,
            risk_reason=risk_reason,
            source_documents=source_documents,
            action=action_text
        )
        """
        Try LLM providers in order for JSON output
        """
        errors = []
        
        # 1. Try DeepSeek
        if self.deepseek_client:
            try:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                errors.append(f"DeepSeek JSON Error: {e}")
        
        # 2. Try Groq
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                errors.append(f"Groq JSON Error: {e}")
        
        # 3. Try Gemini
        if self.gemini_model:
            try:
                combined_prompt = f"{system_prompt}\n\n{user_prompt}"
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.3,
                    response_mime_type="application/json"
                )
                response = self.gemini_model.generate_content(combined_prompt, generation_config=generation_config)
                return response.text.strip()
            except Exception as e:
                errors.append(f"Gemini JSON Error: {e}")

        return "{}" # Return empty JSON compatible string on failure
    
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
            risk_json = self._call_llm_with_fallback_json(
                system_prompt=self._get_risk_assessment_system_prompt(),
                user_prompt=risk_prompt
            )
            
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
            
            print(f"DEBUG CONTEXT: {context[:200]}...")  # Log first 200 chars of context
            
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
                    f"User: {h['question']}\nAssistant: {self._strip_acknowledgement(h['answer'])}"
                    for h in self.chat_history[-3:]  # INCREASE CONTEXT to 3 to help model see flow
                ])
                history_context = f"\n\nPrevious conversation:\n{history_context}\n\n"
            
            # Create prompt for Groq with combined context
            prompt = f"""You are a specialized Neurological Medical Assistant designed for post-discharge patient monitoring.

Your task is to assess the patient's neurological health status based on a short interaction.

RULES:
1. Ask a maximum of {self.max_questions_per_session} simple, yes/no or scale-based questions.
2. Questions must be short, clear, and STRICTLY RELATED to the patient's neurological condition (e.g., headache, vision, balance, confusion, weakness, numbness).
3. If the user reports general symptoms (fever, cough, etc.), acknowledge them but IMMEDIATELY ask if they are experiencing any associated neurological symptoms (e.g., "Do you have a stiff neck or headache with that fever?").
4. Do NOT ask follow-up questions beyond the limit.
5. After collecting answers, produce the final assessment in the specified format.
6. Do NOT include explanations outside the format.
7. Do NOT provide medical diagnosis—only risk assessment and guidance.

CONTEXT:
Current Question Number: {self.question_count + 1}/{self.max_questions_per_session}

MANDATORY SYSTEM RULES (Hidden):
- If {self.question_count + 1} <= {self.max_questions_per_session}: Ask the next question.
- If {self.question_count + 1} > {self.max_questions_per_session}: Stop asking and provide the FINAL OUTPUT.

FINAL OUTPUT FORMAT (User Visible):

Risk Level: <Low / Medium / High>

Action:
- <Clear next step the patient should take>

Reason:
- <Brief justification based on the patient's responses, emphasizing neurological context>


IMPORTANT FOR SYSTEM INTEGRATION (Backend Only):
Regardless of the user-visible output, when you produce the final assessment, you MUST ALSO append a JSON block at the very end of your response (it will be hidden from the user).
Format:
{{
    "risk_level": "LOW|MEDIUM|HIGH",
    "reason": ["reason 1"],
    "action": "action text"
}}

Retrieved medical context (Prioritize NEUROLOGICAL info):
{context[:1000]}

{history_context}

Start directly with the NEXT question. If you have enough info (>=3 questions or at max limit), return the FINAL OUTPUT (Text + JSON)."""

            
            # Call LLM with fallback
            answer = self._call_llm_with_fallback(prompt)

            # Guarantee post-upload acknowledgement on the very first question
            # Only when patient records exist, it's the first question of the day, and no JSON assessment was returned
            if self.patient_retriever is not None and self.question_count == 0:
                lower = answer.lower()
                has_assessment = ("risk_level" in lower and "reason" in lower and "action" in lower)
                if not has_assessment:
                    ack = "Thank you. I’ve reviewed your medical report. Let’s begin today’s check-in."
                    # Prepend acknowledgement before the first question
                    answer = f"{ack}\n{answer}"
            
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

            # Extract action for storage
            action_text = risk_assessment.get("action", "") if risk_assessment else ""

            self.patient_manager.save_chat_message(
                patient_id=self.patient_id,
                question=question,
                answer=answer,
                risk_level=risk_level,
                risk_reason=risk_reason,
                source_documents=source_documents,
                action=action_text
            )
            
            # NUCLEAR FIX: Strip acknowledgement AND hidden JSON from the FINAL ANSWER to be returned
            # This ensures the user sees ONLY the text format they requested
            
            final_answer = self._strip_acknowledgement(answer)
            
            # Remove the JSON block if present at the end
            if "{" in final_answer:
                json_start = final_answer.rfind('{')
                if json_start != -1:
                    # Check if this looks like our hidden JSON block (simple heuristic)
                    possible_json = final_answer[json_start:]
                    if "risk_level" in possible_json and "}" in possible_json:
                        final_answer = final_answer[:json_start].strip()
                        # Clean up any trailing "IMPORTANT..." or "Note:" text if the LLM outputted it before the JSON
                        if "IMPORTANT FOR SYSTEM INTEGRATION" in final_answer:
                             final_answer = final_answer.split("IMPORTANT FOR SYSTEM INTEGRATION")[0].strip()
            
            return {
                "answer": final_answer,
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
