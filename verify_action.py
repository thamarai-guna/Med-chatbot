from patient_manager import get_patient_manager
import json
import inspect
import sys

def test_action_field():
    # Redirect print to file
    with open('log.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        
        pm = get_patient_manager()
        pid = "test_action_patient"
        
        # 1. Register
        print(f"Registering {pid}...")
        try:
            reg_res = pm.register_patient(pid, "Test Patient", "test@example.com", 30, "None")
            print(f"Registration result: {reg_res}")
        except Exception as e:
            print(f"Registration failed with exception: {e}")
        
        print(f"DEBUG: save_chat_message signature: {inspect.signature(pm.save_chat_message)}")
        
        # 2. Save message with Action
        print("Saving message with Action...")
        action_text = "Go to ER immediately"
        try:
            save_res = pm.save_chat_message(
                patient_id=pid,
                question="Headache?",
                answer="Yes",
                risk_level="HIGH",
                risk_reason="Severe pain",
                action=action_text
            )
            print(f"Save result: {save_res}")
        except Exception as e:
            print(f"Save failed with exception: {e}")
        
        # 3. Retrieve history
        print("Retrieving history...")
        history = pm.get_patient_history(pid, limit=1)
        
        if not history:
            print("FAIL: No history found")
            try:
                pm.delete_patient(pid)
            except:
                pass
            return
            
        latest = history[0]
        print(f"Latest message action: {latest.get('action')}")
        
        if latest.get('action') == action_text:
            print("SUCCESS: Action field saved and retrieved correctly")
        else:
            print(f"FAIL: Expected '{action_text}', got '{latest.get('action')}'")
            print(f"Full message: {latest}")
            
        # Cleanup
        pm.delete_patient(pid)

if __name__ == "__main__":
    test_action_field()
