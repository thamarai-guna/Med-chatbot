"""Database models and helper functions."""
from database import get_db

class User:
    """User model for database operations."""
    
    @staticmethod
    def create(email, password, role):
        """Create a new user. Returns user dict if successful, None otherwise."""
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password, role)
                VALUES (?, ?, ?)
            ''', (email, password, role))
            conn.commit()
            
            # Return the created user
            user_id = cursor.lastrowid
            return {'id': user_id, 'email': email, 'role': role}
        except sqlite3.IntegrityError:
            # Email already exists
            return None
        finally:
            conn.close()
    
    @staticmethod
    def find_by_email(email):
        """Find user by email. Returns user dict or None."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    @staticmethod
    def get_all_patients():
        """Get all users with 'patient' role."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email FROM users WHERE role = ? ORDER BY email', ('patient',))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_patient_by_id(patient_id):
        """Get patient details by ID."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, role FROM users WHERE id = ? AND role = ?', 
                      (patient_id, 'patient'))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None


import sqlite3
