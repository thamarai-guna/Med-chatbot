"""
FastAPI Backend Tests
Verifies that API endpoints work correctly and produce same results as Streamlit
"""

import pytest
from fastapi.testclient import TestClient
from backend_api import app
import json
import os

# Create test client
client = TestClient(app)

# Test patient ID (use unique one to avoid conflicts)
TEST_PATIENT_ID = "TEST_PATIENT_001"
TEST_VECTOR_STORE = "DefaultVectorDB"

# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "endpoints" in data

# ============================================================================
# PATIENT MANAGEMENT TESTS
# ============================================================================

def test_register_patient():
    """Test patient registration"""
    response = client.post(
        "/api/patient/register",
        json={
            "patient_id": TEST_PATIENT_ID,
            "name": "Test Patient",
            "email": "test@hospital.com",
            "age": 45,
            "medical_history": "Test history"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["patient_id"] == TEST_PATIENT_ID

def test_register_duplicate_patient():
    """Test registering duplicate patient returns error"""
    # Register first patient
    client.post(
        "/api/patient/register",
        json={
            "patient_id": "DUPLICATE_TEST_001",
            "name": "First",
            "email": "duplicate@hospital.com"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/api/patient/register",
        json={
            "patient_id": "DUPLICATE_TEST_002",
            "name": "Second",
            "email": "duplicate@hospital.com"
        }
    )
    # Should fail due to unique email constraint
    assert response.status_code == 400

def test_get_patient():
    """Test retrieving patient information"""
    # First register
    client.post(
        "/api/patient/register",
        json={
            "patient_id": "GET_TEST_001",
            "name": "Get Test",
            "age": 50
        }
    )
    
    # Then retrieve
    response = client.get(f"/api/patient/GET_TEST_001")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "GET_TEST_001"
    assert data["name"] == "Get Test"
    assert data["age"] == 50

def test_get_nonexistent_patient():
    """Test getting patient that doesn't exist"""
    response = client.get("/api/patient/NONEXISTENT_999")
    assert response.status_code == 404

def test_list_all_patients():
    """Test listing all patients"""
    response = client.get("/api/patient")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "patients" in data
    assert isinstance(data["patients"], list)

# ============================================================================
# CHAT TESTS
# ============================================================================

def test_chat_query():
    """Test chat query endpoint"""
    # Register patient first
    client.post(
        "/api/patient/register",
        json={
            "patient_id": "CHAT_TEST_001",
            "name": "Chat Test Patient"
        }
    )
    
    # Send chat message
    response = client.post(
        "/api/chat/query",
        json={
            "patient_id": "CHAT_TEST_001",
            "message": "What is a common cold?",
            "vector_store_name": TEST_VECTOR_STORE
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "CHAT_TEST_001"
    assert data["question"] == "What is a common cold?"
    assert "answer" in data
    assert "risk_level" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]
    assert "risk_reason" in data
    assert "source_documents" in data
    assert "timestamp" in data

def test_chat_nonexistent_patient():
    """Test chatting with nonexistent patient"""
    response = client.post(
        "/api/chat/query",
        json={
            "patient_id": "NONEXISTENT_999",
            "message": "Hello"
        }
    )
    assert response.status_code == 404

def test_chat_history():
    """Test retrieving chat history"""
    # Register and chat
    patient_id = "HISTORY_TEST_001"
    client.post(
        "/api/patient/register",
        json={"patient_id": patient_id, "name": "History Test"}
    )
    
    # Send a message
    client.post(
        "/api/chat/query",
        json={
            "patient_id": patient_id,
            "message": "Test question",
            "vector_store_name": TEST_VECTOR_STORE
        }
    )
    
    # Get history
    response = client.get(f"/api/chat/history/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == patient_id
    assert "total" in data
    assert "history" in data
    assert len(data["history"]) >= 1
    
    # Check message is in history
    first_msg = data["history"][0]
    assert first_msg["question"] == "Test question"
    assert "answer" in first_msg
    assert "risk_level" in first_msg

def test_clear_chat_history():
    """Test clearing chat history"""
    # Register and chat
    patient_id = "CLEAR_TEST_001"
    client.post(
        "/api/patient/register",
        json={"patient_id": patient_id, "name": "Clear Test"}
    )
    
    # Send message
    client.post(
        "/api/chat/query",
        json={
            "patient_id": patient_id,
            "message": "Test",
            "vector_store_name": TEST_VECTOR_STORE
        }
    )
    
    # Verify history exists
    response = client.get(f"/api/chat/history/{patient_id}")
    assert response.json()["total"] > 0
    
    # Clear history
    response = client.delete(f"/api/chat/history/{patient_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify history is cleared
    response = client.get(f"/api/chat/history/{patient_id}")
    assert response.json()["total"] == 0

# ============================================================================
# RISK ASSESSMENT TESTS
# ============================================================================

def test_risk_summary():
    """Test getting risk summary"""
    # Register and chat
    patient_id = "RISK_TEST_001"
    client.post(
        "/api/patient/register",
        json={"patient_id": patient_id, "name": "Risk Test"}
    )
    
    # Send a few messages to accumulate risk data
    for i in range(3):
        client.post(
            "/api/chat/query",
            json={
                "patient_id": patient_id,
                "message": f"Health question {i}",
                "vector_store_name": TEST_VECTOR_STORE
            }
        )
    
    # Get risk summary
    response = client.get(f"/api/patient/{patient_id}/risk/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == patient_id
    assert "total_queries" in data
    assert data["total_queries"] >= 3
    assert "max_risk_level" in data
    assert "risk_distribution" in data
    
    # Check risk distribution has all levels
    dist = data["risk_distribution"]
    assert "LOW" in dist
    assert "MEDIUM" in dist
    assert "HIGH" in dist
    assert "CRITICAL" in dist

def test_risk_summary_with_days_filter():
    """Test risk summary with days parameter"""
    patient_id = "RISK_DAYS_TEST_001"
    client.post(
        "/api/patient/register",
        json={"patient_id": patient_id, "name": "Risk Days Test"}
    )
    
    # Get summary for different time windows
    response_7d = client.get(f"/api/patient/{patient_id}/risk/summary?days=7")
    response_30d = client.get(f"/api/patient/{patient_id}/risk/summary?days=30")
    
    assert response_7d.status_code == 200
    assert response_30d.status_code == 200

# ============================================================================
# DOCUMENT UPLOAD TESTS
# ============================================================================

def test_upload_documents_without_files():
    """Test document upload fails without files"""
    response = client.post("/api/documents/upload")
    assert response.status_code != 200  # Should fail

def test_document_upload_with_invalid_file():
    """Test document upload with unsupported file type"""
    # Create a temporary invalid file
    response = client.post(
        "/api/documents/upload",
        files={"files": ("test.xyz", b"invalid content")}
    )
    # Should fail due to unsupported file type
    assert response.status_code != 200

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_workflow():
    """Test complete workflow: register → chat → get history → check risk"""
    patient_id = "WORKFLOW_TEST_001"
    
    # 1. Register
    response = client.post(
        "/api/patient/register",
        json={
            "patient_id": patient_id,
            "name": "Workflow Test",
            "age": 40
        }
    )
    assert response.status_code == 200
    
    # 2. Chat
    response = client.post(
        "/api/chat/query",
        json={
            "patient_id": patient_id,
            "message": "What is high blood pressure?",
            "vector_store_name": TEST_VECTOR_STORE
        }
    )
    assert response.status_code == 200
    
    # 3. Get history
    response = client.get(f"/api/chat/history/{patient_id}")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    
    # 4. Get risk summary
    response = client.get(f"/api/patient/{patient_id}/risk/summary")
    assert response.status_code == 200
    assert response.json()["total_queries"] >= 1

def test_multiple_patients_isolation():
    """Test that multiple patients have isolated data"""
    patient1_id = "ISOLATION_TEST_001"
    patient2_id = "ISOLATION_TEST_002"
    
    # Register two patients
    client.post(
        "/api/patient/register",
        json={"patient_id": patient1_id, "name": "Patient 1"}
    )
    client.post(
        "/api/patient/register",
        json={"patient_id": patient2_id, "name": "Patient 2"}
    )
    
    # Patient 1 sends message
    client.post(
        "/api/chat/query",
        json={
            "patient_id": patient1_id,
            "message": "Patient 1 question",
            "vector_store_name": TEST_VECTOR_STORE
        }
    )
    
    # Patient 2 sends message
    client.post(
        "/api/chat/query",
        json={
            "patient_id": patient2_id,
            "message": "Patient 2 question",
            "vector_store_name": TEST_VECTOR_STORE
        }
    )
    
    # Get histories
    hist1 = client.get(f"/api/chat/history/{patient1_id}").json()
    hist2 = client.get(f"/api/chat/history/{patient2_id}").json()
    
    # Verify isolation
    assert hist1["total"] >= 1
    assert hist2["total"] >= 1
    
    # Verify patient 1 doesn't see patient 2's messages
    p1_questions = [msg["question"] for msg in hist1["history"]]
    p2_questions = [msg["question"] for msg in hist2["history"]]
    
    assert "Patient 1 question" in p1_questions
    assert "Patient 1 question" not in p2_questions
    
    assert "Patient 2 question" in p2_questions
    assert "Patient 2 question" not in p1_questions

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    """Run tests with pytest"""
    pytest.main([__file__, "-v", "-s"])
