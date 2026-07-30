
import requests

patient_id = "P001"
url = f"http://localhost:8000/api/chat/history/{patient_id}"

try:
    response = requests.delete(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
