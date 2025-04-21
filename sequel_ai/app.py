from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from dotenv import load_dotenv
from models.db_model import init_db, Chat, Node, Edge
from services.chat_service import process_chat, extract_concepts
from services.graph_service import get_graph_data, create_sample_graph
import requests
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sequel_ai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
init_db(app)

# Create sample graph data on startup
with app.app_context():
    create_sample_graph()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Process the chat message - now returns both response and concepts
    result = process_chat(message)
    
    # No need to call extract_concepts separately - it's done inside process_chat
    
    return jsonify(result)

@app.route('/api/graph_data')
def get_graph():
    return jsonify(get_graph_data())

@app.route('/toggle_graph_mode')
def toggle_graph_mode():
    return redirect(url_for('graph'))

@app.route('/debug/api_test')
def debug_api_test():
    """Debug endpoint to directly test the OpenRouter API connection."""
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    MODEL = os.environ.get("MODEL", "openai/gpt-3.5-turbo")
    
    if not OPENROUTER_API_KEY:
        return jsonify({
            'error': 'No API key set',
            'instructions': 'Set OPENROUTER_API_KEY in .env file'
        }), 400
    
    try:
        # Make request to OpenRouter API with simplified request
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000", 
            "X-Title": "Sequel AI Debug"
        }
        
        # Even simpler request with minimal parameters
        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello!"
                }
            ]
        }
        
        # Make the API request
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", 
            headers=headers, 
            json=data,
            timeout=15
        )
        
        # Return both the response object and its content for debugging
        return jsonify({
            'status_code': resp.status_code,
            'headers': dict(resp.headers),
            'body': resp.text,
            'parsed': resp.json() if resp.status_code == 200 else None,
            'key_preview': f"{OPENROUTER_API_KEY[:5]}...{OPENROUTER_API_KEY[-5:]}",
            'model': MODEL
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 