import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_stream():
    print("Testing streaming endpoint...")
    
    # 1. Register a test patient first
    reg_url = f"{BASE_URL}/api/patient/register"
    try:
        resp = requests.post(reg_url, json={
            "patient_id": "stream_test_user",
            "name": "Stream Tester",
            "email": "stream@test.com",
            "age": 25,
            "medical_history": "None"
        })
        print(f"Registration status: {resp.status_code}")
        print(f"Registration response: {resp.text}")
    except Exception as e:
        print(f"Registration failed: {e}")

    # 2. Hit the streaming endpoint
    # Note: requests.get with stream=True
    try:
        url = f"{BASE_URL}/api/chat/stream"
        params = {"patient_id": "patient1", "message": "I have a headache"}
        
        print(f"Connecting to {url} with params {params}...")
        
        # We need a large timeout because RAG can be slow
        with requests.get(url, params=params, stream=True, timeout=30) as r:
            if r.status_code == 200:
                print("Connection successful (200 OK)")
                print("Receiving chunks:")
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        text = chunk.decode('utf-8')
                        print(f"[{len(text)} chars]", end="", flush=True)
                print("\nStream completed successfully.")
            else:
                print(f"Failed with status code: {r.status_code}")
                print(r.text)
                
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_stream()
