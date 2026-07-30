from patient_manager import get_patient_manager
import sys

def check_and_create_patient():
    pm = get_patient_manager()
    pid = "patient1"
    
    print(f"Checking for patient: {pid}")
    p = pm.get_patient(pid)
    
    if p:
        print(f"Patient found: {p}")
    else:
        print(f"Patient not found. Creating {pid}...")
        try:
            # register_patient(patient_id, name, email, age, medical_history)
            res = pm.register_patient(pid, "Demo Patient", "patient1@demo.com", 35, "None")
            print(f"Registration result: {res}")
        except Exception as e:
            print(f"Failed to register: {e}")

if __name__ == "__main__":
    check_and_create_patient()
