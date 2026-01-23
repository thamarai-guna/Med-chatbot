# Clinical Monitoring System for Post-Discharge Neurological Patient Assessment
# Strict guidelines enforcement: Medical reports MANDATORY before ANY monitoring

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# System prompt for clinical monitoring
CLINICAL_MONITORING_SYSTEM_PROMPT = """You are an AI assistant for post-discharge neurological patient monitoring.

CRITICAL PRECONDITION:
You operate ONLY after patient medical reports are available.
Never provide monitoring questions without verified medical history.

ROLE:
- Monitor neurological symptoms in patients following discharge
- Ask targeted questions about specific symptom categories
- Assess risk level based on symptom patterns
- Enforce strict clinical guidelines in all responses

RESPONSE FORMAT:
All responses MUST be valid JSON. No prose, no markdown, pure JSON structure only.

QUESTION STRUCTURE:
- Ask ONE question at a time
- Questions must be specific to neurological symptoms
- Allow different answer types: YES_NO, SCALE_0_10, SHORT_TEXT
- Prevent repetition: never ask the same question twice
- Use previous answers to inform subsequent questions
- Ask 3-6 questions maximum per session

SYMPTOM CATEGORIES:
- Headaches and pain patterns
- Motor function changes
- Sensory changes
- Cognitive changes
- Balance and coordination
- Sleep patterns
- Mood changes

RISK ASSESSMENT:
After all questions, generate final assessment with:
- Risk Level: LOW, MEDIUM, or HIGH (never CRITICAL)
- Reason: 2-3 sentence explanation
- Action: Recommended next step
- JSON format: {"risk_level": "...", "reason": "...", "action": "..."}

SAFETY RULES:
1. Never diagnose - only assess risk based on symptom reports
2. Never recommend medication changes
3. Always recommend medical consultation for HIGH risk
4. Maintain patient privacy in all responses
5. Use clinical but understandable language"""


def create_question_generation_prompt(
    patient_history: str,
    previous_answers: Dict[str, Any],
    current_question_number: int,
    max_questions: int,
    retrieved_medical_guidance: str
) -> str:
    """
    Create a prompt for generating the next monitoring question.
    
    Parameters:
    - patient_history: Patient's medical background
    - previous_answers: Answers to previous questions
    - current_question_number: Current question count (1-based)
    - max_questions: Maximum questions for this session
    - retrieved_medical_guidance: Relevant medical context from RAG
    """
    
    answers_summary = "\n".join(
        f"Q{i+1}: {qa.get('question', 'Unknown')}\n"
        f"Answer ({qa.get('answer_type', 'UNKNOWN')}): {qa.get('answer', 'No response')}"
        for i, qa in enumerate(previous_answers.get('answered_questions', []))
    ) if previous_answers.get('answered_questions') else "No previous answers yet."
    
    prompt = f"""You are assisting with neurological symptom monitoring.

PATIENT CONTEXT:
Medical History: {patient_history}

MEDICAL GUIDANCE:
{retrieved_medical_guidance}

PREVIOUS RESPONSES:
{answers_summary}

QUESTION {current_question_number} OF {max_questions}:
Generate the next monitoring question following these rules:
1. Ask about a neurological symptom NOT previously asked
2. Choose appropriate answer type (YES_NO, SCALE_0_10, or SHORT_TEXT)
3. Make it specific and measurable
4. Use simple, patient-friendly language
5. Build on previous answers if relevant

Return ONLY valid JSON:
{{
    "question": "Your question here",
    "answer_type": "YES_NO or SCALE_0_10 or SHORT_TEXT",
    "explanation": "Why we're asking this based on context"
}}"""
    
    return prompt


def create_risk_assessment_prompt(
    patient_history: str,
    monitoring_responses: Dict[str, Any],
    retrieved_medical_guidance: str
) -> str:
    """
    Create a prompt for final risk assessment based on all monitoring responses.
    
    Parameters:
    - patient_history: Patient's medical background
    - monitoring_responses: All Q and A pairs from the session
    - retrieved_medical_guidance: Relevant medical context from RAG
    """
    
    responses_text = "\n".join(
        f"Q: {qa.get('question', 'Unknown')}\n"
        f"A: {qa.get('answer', 'No response')} ({qa.get('answer_type', 'UNKNOWN')})"
        for qa in monitoring_responses.get('answered_questions', [])
    ) if monitoring_responses.get('answered_questions') else "No responses recorded."
    
    prompt = f"""You are a clinical assessment expert for neurological monitoring.

PATIENT CONTEXT:
Medical History: {patient_history}

MEDICAL GUIDANCE:
{retrieved_medical_guidance}

MONITORING SESSION RESPONSES:
{responses_text}

ASSESSMENT TASK:
Based on the symptom responses provided, generate a clinical risk assessment.

CRITICAL RULES:
1. Risk Level must be exactly one of: LOW, MEDIUM, HIGH
2. LOW: No concerning symptoms or well-controlled symptoms
3. MEDIUM: Some concerning symptoms requiring follow-up
4. HIGH: Significant symptoms requiring urgent medical evaluation
5. Always recommend medical consultation for MEDIUM and HIGH

Generate ONLY valid JSON with no additional text:
{{
    "risk_level": "LOW or MEDIUM or HIGH",
    "reason": "2-3 sentence clinical reasoning",
    "action": "Recommended next step for patient provider"
}}"""
    
    return prompt


class QuestionTracker:
    """Track questions asked and prevent repetition within a monitoring session."""
    
    def __init__(self):
        self.asked_questions: List[str] = []
        self.negative_responses: Dict[str, int] = {}
    
    def add_question(self, question: str) -> None:
        """Record that a question was asked."""
        self.asked_questions.append(question)
    
    def mark_negative_response(self, question: str) -> None:
        """Mark that a question received a NO answer."""
        self.negative_responses[question] = self.negative_responses.get(question, 0) + 1
    
    def has_asked(self, question: str) -> bool:
        """Check if question has been asked in this session."""
        return question in self.asked_questions
    
    def can_ask_more(self, max_questions: int) -> bool:
        """Check if we can ask more questions."""
        return len(self.asked_questions) < max_questions
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of questions asked so far."""
        return {
            "total_questions_asked": len(self.asked_questions),
            "questions": self.asked_questions,
            "negative_responses": self.negative_responses
        }


class MedicalReportValidator:
    """Validate that medical reports exist before allowing monitoring."""
    
    NO_REPORT_MESSAGE = "Medical reports are required before symptom monitoring can begin."
    PLACEHOLDER_TEXTS = [
        "no previous history",
        "no medical history",
        "unknown",
        "not provided",
        "n/a"
    ]
    
    @staticmethod
    def check_report_availability(patient_history: str) -> bool:
        """
        Check if patient has a valid medical report.
        
        Returns True only if:
        1. History exists and is not empty
        2. History does NOT contain placeholder text
        3. History has meaningful length greater than 20 characters
        """
        if not patient_history:
            return False
        
        history_lower = patient_history.lower().strip()
        
        if any(placeholder in history_lower for placeholder in MedicalReportValidator.PLACEHOLDER_TEXTS):
            return False
        
        if len(history_lower) < 20:
            return False
        
        return True
    
    @staticmethod
    def get_blocking_response() -> Dict[str, Any]:
        """Get the blocking response when medical report is missing."""
        return {
            "status": "error",
            "code": "NO_MEDICAL_REPORT",
            "message": MedicalReportValidator.NO_REPORT_MESSAGE,
            "action": "Please upload patient medical reports before starting monitoring",
            "timestamp": datetime.utcnow().isoformat()
        }


def validate_json_response(response_text: str) -> tuple[bool, Dict[str, Any]]:
    """
    Validate and parse JSON response from LLM.
    
    Returns: is valid, parsed data
    """
    try:
        data = json.loads(response_text)
        return True, data
    except json.JSONDecodeError as e:
        return False, {"error": str(e), "raw_response": response_text}


def validate_risk_level(risk_level: str) -> bool:
    """Validate that risk level is one of the allowed values."""
    allowed_levels = ["LOW", "MEDIUM", "HIGH"]
    return risk_level.upper() in allowed_levels


def validate_answer_type(answer_type: str) -> bool:
    """Validate that answer type is one of the allowed values."""
    allowed_types = ["YES_NO", "SCALE_0_10", "SHORT_TEXT"]
    return answer_type.upper() in allowed_types
