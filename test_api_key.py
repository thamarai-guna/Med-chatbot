#!/usr/bin/env python3
"""Test Groq API Key"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

if not api_key:
    print('❌ GROQ_API_KEY not found in .env')
    exit(1)

print(f'✅ API Key found: {api_key[:30]}...')
print('Testing API connection...')

url = 'https://api.groq.com/openai/v1/chat/completions'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
payload = {
    'model': 'llama-3.3-70b-versatile',  # Latest Llama model
    'messages': [{'role': 'user', 'content': 'Say hello in one word'}],
    'max_tokens': 20
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        result = response.json()['choices'][0]['message']['content']
        print(f'✅ API Test PASSED!')
        print(f'Response: {result}')
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'Details: {response.text}')
except Exception as e:
    print(f'❌ Connection Error: {str(e)}')
