import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key[:20]}...")

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "user",
            "content": "Hello, what is 2+2?"
        }
    ],
    "max_tokens": 100,
    "temperature": 0.7
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    print(f"✅ SUCCESS: {data['choices'][0]['message']['content']}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response Status: {e.response.status_code}")
        print(f"Response Body: {e.response.text}")
