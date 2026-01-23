"""
Patient Management System
Handles patient registration, authentication, and data isolation with SQLite
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

DB_PATH = "patient_data.db"


class PatientManager:
    """
    Manages patient data with SQLite backend
    Ensures data isolation and secure patient records
    """
    
    def __init__(self):
        """Initialize database and create tables if needed"""
        self.db_path = DB_PATH
        self._init_database()
    
    def _init_database(self):
        """Create database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                medical_history TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat history table - per patient
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                risk_level TEXT,
                risk_reason TEXT,
                source_documents TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )
        ''')
        
        # Risk assessments table - for medical audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                question TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_reason TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_patient(self, patient_id: str, name: str, email: Optional[str] = None, 
                        age: Optional[int] = None, medical_history: str = "") -> Dict[str, Any]:
        """
        Register a new patient
        
        Args:
            patient_id: Unique identifier for patient (e.g., 'P001', 'patient_123')
            name: Patient name
            email: Optional email
            age: Optional age
            medical_history: Optional medical history notes
            
        Returns:
            Success response with patient details
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO patients (patient_id, name, email, age, medical_history)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, name, email, age, medical_history))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Patient {name} registered successfully",
                "patient_id": patient_id
            }
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"success": False, "message": "Patient ID or email already exists"}
            return {"success": False, "message": str(e)}
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve patient information
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient dict or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "patient_id": row[0],
            "name": row[1],
            "email": row[2],
            "age": row[3],
            "medical_history": row[4],
            "created_at": row[5],
            "last_accessed": row[6]
        }
    
    def get_all_patients(self) -> List[Dict[str, Any]]:
        """Get list of all registered patients"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT patient_id, name, email, age, created_at FROM patients ORDER BY last_accessed DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "patient_id": row[0],
                "name": row[1],
                "email": row[2],
                "age": row[3],
                "created_at": row[4]
            }
            for row in rows
        ]
    
    def save_chat_message(self, patient_id: str, question: str, answer: str, 
                         risk_level: str, risk_reason: str, source_documents: List[str] = None) -> bool:
        """
        Save chat message to patient history
        
        Args:
            patient_id: Patient identifier
            question: User question
            answer: LLM answer
            risk_level: Medical risk level
            risk_reason: Risk explanation
            source_documents: List of source documents
            
        Returns:
            Success status
        """
        # Verify patient exists
        if not self.get_patient(patient_id):
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            docs_json = json.dumps(source_documents or [])
            
            cursor.execute('''
                INSERT INTO chat_history 
                (patient_id, question, answer, risk_level, risk_reason, source_documents)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, question, answer, risk_level, risk_reason, docs_json))
            
            # Update last_accessed timestamp
            cursor.execute('UPDATE patients SET last_accessed = CURRENT_TIMESTAMP WHERE patient_id = ?', 
                          (patient_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return False
    
    def get_patient_history(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a specific patient
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of recent messages
            
        Returns:
            List of chat messages (most recent first)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, answer, risk_level, risk_reason, source_documents, timestamp
            FROM chat_history
            WHERE patient_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (patient_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "risk_level": row[3],
                "risk_reason": row[4],
                "source_documents": json.loads(row[5]) if row[5] else [],
                "timestamp": row[6]
            }
            for row in reversed(rows)  # Return in chronological order
        ]
    
    def get_patient_risk_summary(self, patient_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get risk assessment summary for patient
        
        Args:
            patient_id: Patient identifier
            days: Number of days to look back
            
        Returns:
            Risk statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get risk levels from recent history
        cursor.execute('''
            SELECT risk_level, COUNT(*) as count
            FROM chat_history
            WHERE patient_id = ? 
            AND timestamp > datetime('now', '-' || ? || ' days')
            GROUP BY risk_level
        ''', (patient_id, days))
        
        risk_counts = cursor.fetchall()
        conn.close()
        
        summary = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0,
            "UNKNOWN": 0
        }
        
        for risk_level, count in risk_counts:
            if risk_level in summary:
                summary[risk_level] = count
        
        return {
            "patient_id": patient_id,
            "risk_distribution": summary,
            "total_queries": sum(summary.values()),
            "max_risk_level": next((level for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] 
                                    if summary[level] > 0), "UNKNOWN")
        }
    
    def clear_patient_history(self, patient_id: str) -> bool:
        """
        Clear all chat history for a patient (e.g., for privacy)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM chat_history WHERE patient_id = ?', (patient_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete patient and all associated data (GDPR compliance)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Foreign key cascade will delete history and assessments
            cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting patient: {e}")
            return False


# Singleton instance
_patient_manager = None

def get_patient_manager() -> PatientManager:
    """Get or create singleton PatientManager instance"""
    global _patient_manager
    if _patient_manager is None:
        _patient_manager = PatientManager()
    return _patient_manager
