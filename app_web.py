from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found")

app = Flask(__name__)
client = Groq(api_key=api_key)
model = "llama-3.3-70b-versatile"
chat_sessions = {}

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Chatbot</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            .container { background: white; border-radius: 10px; width: 90%; max-width: 700px; height: 80vh; display: flex; flex-direction: column; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
            .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; }
            .chat { flex: 1; overflow-y: auto; padding: 20px; background: #f5f5f5; }
            .msg { margin: 10px 0; display: flex; }
            .user { justify-content: flex-end; }
            .bubble { max-width: 70%; padding: 10px 15px; border-radius: 10px; word-wrap: break-word; }
            .user .bubble { background: #667eea; color: white; }
            .bot .bubble { background: #e0e0e0; color: #333; }
            .input-area { padding: 15px; border-top: 1px solid #ddd; display: flex; gap: 10px; }
            input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #764ba2; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Medical Chatbot</h1>
                <p>Powered by Groq AI</p>
            </div>
            <div class="chat" id="chat"></div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Ask a question..." autofocus>
                <button onclick="send()">Send</button>
            </div>
        </div>
        <script>
            const sid = 's' + Date.now();
            const chat = document.getElementById('chat');
            const input = document.getElementById('input');
            input.addEventListener('keypress', e => {
                if(e.key === 'Enter') send();
            });
            function add(text, type) {
                const m = document.createElement('div');
                m.className = 'msg ' + type;
                const b = document.createElement('div');
                b.className = 'bubble';
                b.textContent = text;
                m.appendChild(b);
                chat.appendChild(m);
                chat.scrollTop = chat.scrollHeight;
            }
            async function send() {
                const msg = input.value.trim();
                if(!msg) return;
                input.value = '';
                input.disabled = true;
                add(msg, 'user');
                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: msg, session_id: sid})
                    });
                    const data = await res.json();
                    if(data.status === 'success') add(data.message, 'bot');
                    else add('Error: ' + data.message, 'bot');
                } catch(e) {
                    add('Error: ' + e.message, 'bot');
                } finally {
                    input.disabled = false;
                    input.focus();
                }
            }
            window.addEventListener('load', () => {
                add('Hello! Ask me anything about health and medical information.', 'bot');
            });
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.json
        msg = data.get('message', '').strip()
        sid = data.get('session_id', 'default')
        
        if not msg:
            return jsonify({'status': 'error', 'message': 'Empty'}), 400
        
        if sid not in chat_sessions:
            chat_sessions[sid] = []
        
        messages = [
            {'role': 'system', 'content': 'You are a helpful medical chatbot.'}
        ]
        messages.extend(chat_sessions[sid][-6:])
        messages.append({'role': 'user', 'content': msg})
        
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        bot_msg = resp.choices[0].message.content
        chat_sessions[sid].append({'role': 'user', 'content': msg})
        chat_sessions[sid].append({'role': 'assistant', 'content': bot_msg})
        
        return jsonify({'status': 'success', 'message': bot_msg})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("\nMedical Chatbot - http://localhost:8000\n")
    app.run(host='127.0.0.1', port=8000, debug=True, use_reloader=False)
