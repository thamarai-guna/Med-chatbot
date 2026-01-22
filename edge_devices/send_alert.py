"""
Edge Device Alert Simulator

This script simulates an edge device sending alerts to the central server.
Use this for testing and demo purposes only.

Usage:
    python send_alert.py
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
EDGE_API_KEY = "edge-device-secret-key-change-in-production"  # Must match backend .env


def send_alert(patient_id: int, alert_type: str, message: str, severity: str, source: str):
    """
    Send an alert to the central server.
    
    Args:
        patient_id: ID of the patient
        alert_type: Type of alert (VITALS_ABNORMAL, COMA_MOVEMENT_DETECTED, HIGH_RISK_FROM_CHATBOT)
        message: Human-readable message
        severity: LOW, MEDIUM, or HIGH
        source: vitals_edge, coma_edge, or ai_chatbot
    """
    url = f"{API_BASE_URL}/alerts"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": EDGE_API_KEY
    }
    
    payload = {
        "patient_id": patient_id,
        "alert_type": alert_type,
        "message": message,
        "severity": severity,
        "source": source
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"Sending alert to {url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"{'='*60}\n")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print("✅ Alert sent successfully!")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            return True
        else:
            print(f"❌ Failed to send alert")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}\n")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Unable to connect to backend server")
        print("Please ensure the backend server is running on http://localhost:8000\n")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        return False


def simulate_vitals_alert():
    """Simulate a vitals abnormality alert"""
    print("\n🩺 Simulating VITALS ABNORMALITY alert...")
    send_alert(
        patient_id=1,
        alert_type="VITALS_ABNORMAL",
        message="Heart rate elevated: 125 bpm (threshold: 100 bpm)",
        severity="MEDIUM",
        source="vitals_edge"
    )


def simulate_coma_alert():
    """Simulate a coma patient movement alert"""
    print("\n👁️ Simulating COMA MOVEMENT alert...")
    send_alert(
        patient_id=1,
        alert_type="COMA_MOVEMENT_DETECTED",
        message="Sudden movement detected in coma patient - Bed A-101",
        severity="HIGH",
        source="coma_edge"
    )


def simulate_chatbot_alert():
    """Simulate a high-risk chatbot alert"""
    print("\n🤖 Simulating CHATBOT HIGH RISK alert...")
    send_alert(
        patient_id=1,
        alert_type="HIGH_RISK_FROM_CHATBOT",
        message="Patient reported severe headache and dizziness - Risk: HIGH",
        severity="HIGH",
        source="ai_chatbot"
    )


def interactive_menu():
    """Interactive menu for sending alerts"""
    print("\n" + "="*60)
    print("     EDGE DEVICE ALERT SIMULATOR")
    print("="*60)
    print("\nSelect alert type to simulate:")
    print("1. Vitals Abnormality (MEDIUM severity)")
    print("2. Coma Patient Movement (HIGH severity)")
    print("3. Chatbot High Risk (HIGH severity)")
    print("4. Custom Alert")
    print("5. Send All Test Alerts")
    print("0. Exit")
    print("-"*60)
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    if choice == "1":
        simulate_vitals_alert()
    elif choice == "2":
        simulate_coma_alert()
    elif choice == "3":
        simulate_chatbot_alert()
    elif choice == "4":
        custom_alert()
    elif choice == "5":
        print("\n📨 Sending all test alerts...\n")
        simulate_vitals_alert()
        simulate_coma_alert()
        simulate_chatbot_alert()
    elif choice == "0":
        print("\n👋 Exiting...\n")
        return False
    else:
        print("\n❌ Invalid choice. Please try again.\n")
    
    return True


def custom_alert():
    """Create and send a custom alert"""
    print("\n📝 Create Custom Alert")
    print("-"*60)
    
    try:
        patient_id = int(input("Patient ID: "))
        
        print("\nAlert Types:")
        print("1. VITALS_ABNORMAL")
        print("2. COMA_MOVEMENT_DETECTED")
        print("3. HIGH_RISK_FROM_CHATBOT")
        alert_choice = input("Select alert type (1-3): ").strip()
        
        alert_types = {
            "1": "VITALS_ABNORMAL",
            "2": "COMA_MOVEMENT_DETECTED",
            "3": "HIGH_RISK_FROM_CHATBOT"
        }
        alert_type = alert_types.get(alert_choice, "VITALS_ABNORMAL")
        
        message = input("Alert message: ")
        
        print("\nSeverity:")
        print("1. LOW")
        print("2. MEDIUM")
        print("3. HIGH")
        severity_choice = input("Select severity (1-3): ").strip()
        
        severities = {"1": "LOW", "2": "MEDIUM", "3": "HIGH"}
        severity = severities.get(severity_choice, "MEDIUM")
        
        print("\nSource:")
        print("1. vitals_edge")
        print("2. coma_edge")
        print("3. ai_chatbot")
        source_choice = input("Select source (1-3): ").strip()
        
        sources = {"1": "vitals_edge", "2": "coma_edge", "3": "ai_chatbot"}
        source = sources.get(source_choice, "vitals_edge")
        
        send_alert(patient_id, alert_type, message, severity, source)
        
    except ValueError:
        print("\n❌ Invalid input. Please try again.\n")
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled.\n")


if __name__ == "__main__":
    print("\n🚀 Starting Edge Device Alert Simulator...")
    print("Backend URL:", API_BASE_URL)
    print("API Key:", EDGE_API_KEY[:20] + "..." if len(EDGE_API_KEY) > 20 else EDGE_API_KEY)
    
    # Check if backend is reachable
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            print("✅ Backend server is online\n")
        else:
            print("⚠️  Backend server returned unexpected status\n")
    except:
        print("❌ Warning: Cannot reach backend server")
        print("Please start the backend server first: uvicorn app.main:app --reload\n")
    
    # Interactive menu loop
    try:
        while interactive_menu():
            input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
