from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from models.db_model import init_db, Chat, Node, Edge
from services.chat_service import process_chat, extract_concepts
from services.graph_service import get_graph_data, create_sample_graph

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
    
    # Process the chat message
    response = process_chat(message)
    
    # Extract concepts and store in the graph
    extract_concepts(message, response)
    
    return jsonify({'response': response})

@app.route('/api/graph_data')
def get_graph():
    return jsonify(get_graph_data())

@app.route('/toggle_graph_mode')
def toggle_graph_mode():
    return redirect(url_for('graph'))

if __name__ == '__main__':
    app.run(debug=True) 