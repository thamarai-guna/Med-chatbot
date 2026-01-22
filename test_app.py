from app_web import app
import json

with app.test_client() as client:
    print("Testing home endpoint...")
    response = client.get('/')
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Has HTML: {'DOCTYPE' in response.get_data(as_text=True)}")
    
    print("\nTesting chat API...")
    response = client.post('/api/chat', 
        data=json.dumps({'message': 'What is diabetes?', 'session_id': 'test'}),
        content_type='application/json'
    )
    print(f"✓ Status: {response.status_code}")
    data = json.loads(response.get_data(as_text=True))
    print(f"✓ Status: {data.get('status')}")
    if data.get('status') == 'success':
        print(f"✓ Got response: {data['message'][:100]}...")
    else:
        print(f"✗ Error: {data.get('message')}")

