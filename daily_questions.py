"""
Daily Question Generator for Patients
Generates personalized symptom monitoring questions
Uses patient records + shared medical knowledge
"""



import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai
from patient_manager import get_patient_manager

load_dotenv()


class DailyQuestionGenerator:
    """
    Generates personalized daily questions for patient symptom monitoring
    Based on:
    - Patient's uploaded medical records
    - Shared neurology book context
    - Previous daily answers
    - Detected risk trends
    """
    
    def __init__(self, patient_id: str):
        """
        Initialize question generator for a specific patient
        
        Args:
            patient_id: Patient identifier
        """
        self.patient_id = patient_id
        self.patient_manager = get_patient_manager()
        
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
            raise ValueError(f"Patient {patient_id} not found")
        
        self.patient_info = patient
    
    def _call_llm_with_fallback(self, prompt: str) -> str:
        """
        Try LLM providers in order: DeepSeek -> Groq -> Gemini
        """
        # 1. Try DeepSeek (Primary)
        if self.deepseek_client:
            try:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ DeepSeek failed: {e}. Trying Groq...")

        # 2. Try Groq (Secondary)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ Groq failed: {e}. Trying Gemini...")

        # 3. Try Gemini (Tertiary)
        if self.gemini_model:
            try:
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.7,
                    response_mime_type="application/json"
                )
                response = self.gemini_model.generate_content(prompt, generation_config=generation_config)
                return response.text.strip()
            except Exception as e:
                print(f"⚠️ Gemini failed: {e}.")

        return "{}" # Return empty JSON on total failure
    
    def _get_patient_history_summary(self, days: int = 7) -> str:
        """
        Get summary of patient's recent chat history
        
        Args:
            days: Number of days to look back
        
        Returns:
            Text summary of recent questions and concerns
        """
        history = self.patient_manager.get_patient_history(self.patient_id, limit=20)
        
        if not history:
            return "No previous chat history available."
        
        # Summarize recent questions
        recent_concerns = []
        for item in history[:10]:  # Last 10 interactions
            recent_concerns.append(f"- {item['question']} (Risk: {item['risk_level']})")
        
        return "\n".join(recent_concerns)
    
    def _get_risk_trend(self, days: int = 7) -> str:
        """
        Get risk level trend for patient
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Text description of risk trend
        """
        risk_summary = self.patient_manager.get_patient_risk_summary(self.patient_id, days=days)
        
        max_risk = risk_summary.get('max_risk_level', 'UNKNOWN')
        distribution = risk_summary.get('risk_distribution', {})
        
        critical_count = distribution.get('CRITICAL', 0)
        high_count = distribution.get('HIGH', 0)
        
        if critical_count > 0:
            return f"CRITICAL risk detected in last {days} days ({critical_count} instances)"
        elif high_count > 0:
            return f"HIGH risk detected in last {days} days ({high_count} instances)"
        elif max_risk in ['MEDIUM', 'LOW']:
            return f"Stable condition (max risk: {max_risk})"
        else:
            return "No significant risk trends"
    
    def generate_daily_question(self) -> Dict[str, Any]:
        """
        Generate a personalized daily symptom question
        
        Returns:
            dict with:
                - question: The question text
                - question_type: "yes_no", "numeric_scale", or "text"
                - options: List of possible answers (for yes_no or scale)
                - context: Why this question is being asked
                - category: Symptom category (e.g., "headache", "mobility", "cognitive")
        """
        
        # Get patient context
        medical_history = self.patient_info.get('medical_history', 'No medical history recorded')
        recent_concerns = self._get_patient_history_summary(days=7)
        risk_trend = self._get_risk_trend(days=7)
        
        # Create prompt for question generation
        prompt = f"""You are a medical AI generating a daily symptom monitoring question for a patient.

PATIENT CONTEXT:
- Patient ID: {self.patient_id}
- Medical History: {medical_history}
- Recent Concerns (last 7 days):
{recent_concerns}
- Risk Trend: {risk_trend}

RULES FOR QUESTION GENERATION:
1. Questions must be SIMPLE and easy to answer
2. Prefer YES/NO questions or numeric scales (1-10)
3. Focus on ONE specific symptom or concern
4. Base questions on patient's medical history and recent concerns
5. Avoid repetitive questions - vary the focus
6. Use plain language, avoid medical jargon
7. Questions should help monitor symptom progression
8. Be respectful and non-alarming

QUESTION TYPES TO USE:
- Yes/No: "Have you experienced [symptom] today?"
- Numeric Scale: "Rate your [symptom] on a scale of 1-10"
- Frequency: "How many times did [symptom] occur today?"

RESPONSE FORMAT (JSON only):
{{
  "question": "Your question text here",
  "question_type": "yes_no OR numeric_scale OR frequency",
  "options": ["Yes", "No"] OR ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
  "context": "Brief explanation of why this question matters",
  "category": "headache OR mobility OR cognitive OR pain OR other"
}}

Generate ONE daily question now:"""
        
        # Call LLM with fallback
        response_text = self._call_llm_with_fallback(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle potential markdown formatting)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            question_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["question", "question_type", "options", "context", "category"]
            for field in required_fields:
                if field not in question_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add metadata
            question_data["generated_at"] = datetime.now().isoformat()
            question_data["patient_id"] = self.patient_id
            
            return question_data
        
        except Exception as e:
            # Fallback to generic question if LLM fails
            print(f"Error parsing DeepSeek response: {e}")
            return self._get_fallback_question()
    
    def _get_fallback_question(self) -> Dict[str, Any]:
        """
        Fallback question if LLM generation fails
        
        Returns:
            Generic daily question
        """
        return {
            "question": "How are you feeling today compared to yesterday?",
            "question_type": "numeric_scale",
            "options": ["Much Worse", "Worse", "Same", "Better", "Much Better"],
            "context": "General daily wellness check",
            "category": "general",
            "generated_at": datetime.now().isoformat(),
            "patient_id": self.patient_id,
            "fallback": True
        }
    
    def save_daily_answer(self, question: str, answer: str, question_metadata: Optional[Dict] = None) -> bool:
        """
        Save patient's answer to daily question
        
        Args:
            question: The question that was asked
            answer: Patient's answer
            question_metadata: Optional metadata about the question
        
        Returns:
            True if saved successfully
        """
        try:
            # Save as a special chat message with marker
            self.patient_manager.save_chat_message(
                patient_id=self.patient_id,
                question=f"[DAILY_QUESTION] {question}",
                answer=f"[DAILY_ANSWER] {answer}",
                risk_level="MONITORING",
                risk_reason="Daily symptom monitoring",
                source_documents=[json.dumps(question_metadata)] if question_metadata else []
            )
            return True
        except Exception as e:
            print(f"Error saving daily answer: {e}")
            return False
    
    def get_recent_daily_answers(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get patient's recent daily question answers
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of daily Q&A records
        """
        history = self.patient_manager.get_patient_history(self.patient_id, limit=50)
        
        daily_answers = []
        for item in history:
            if item['question'].startswith('[DAILY_QUESTION]'):
                daily_answers.append({
                    "question": item['question'].replace('[DAILY_QUESTION] ', ''),
                    "answer": item['answer'].replace('[DAILY_ANSWER] ', ''),
                    "timestamp": item['timestamp']
                })
        
        return daily_answers[:days]


def generate_question_for_patient(patient_id: str) -> Dict[str, Any]:
    """
    Standalone function to generate daily question
    
    Args:
        patient_id: Patient identifier
    
    Returns:
        Question dict
    """
    generator = DailyQuestionGenerator(patient_id)
    return generator.generate_daily_question()


if __name__ == "__main__":
    """
    Test daily question generation
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python daily_questions.py <patient_id>")
        sys.exit(1)
    
    patient_id = sys.argv[1]
    
    print(f"Generating daily question for patient: {patient_id}")
    print("=" * 60)
    
    try:
        generator = DailyQuestionGenerator(patient_id)
        question = generator.generate_daily_question()
        
        print("\nGENERATED QUESTION:")
        print(json.dumps(question, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")
