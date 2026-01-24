
import requests
import time

max_retries = 5
for i in range(max_retries):
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is HEALTHY")
            exit(0)
    except:
        print(f"Waiting for backend... ({i+1}/{max_retries})")
        time.sleep(2)
        
print("❌ Backend is NOT responding")
