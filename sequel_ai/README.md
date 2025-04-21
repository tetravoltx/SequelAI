# Sequel AI

A conversational AI interface with graph visualization mode, built with Flask and Sigma.js.

## Features

- Chat interface with AI responses using OpenRouter API (Gemini model)
- Graph visualization of concepts extracted from conversations
- Interactive knowledge graph with Sigma.js
- SQLite database for storing chat history and graph data

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/MacOS
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Rename `.env.example` to `.env`
   - Add your OpenRouter API key in the `.env` file:
     ```
     OPENROUTER_API_KEY=your_api_key_here
     ```

## Running the Application

```
flask run
```

Access the application at http://127.0.0.1:5000/

## Project Structure

- `app.py`: Main Flask application file
- `models/`: Database models
  - `db_model.py`: SQLAlchemy models for Chat, Node, and Edge
- `services/`: Application services
  - `chat_service.py`: Handles chat processing and concept extraction
  - `graph_service.py`: Manages graph data retrieval and creation
- `templates/`: HTML templates
  - `index.html`: Main chat interface
  - `graph.html`: Graph visualization interface
- `static/`: Static assets (CSS, JS, images)

## Usage

1. Start on the main page and type a message in the chat input
2. Click the Send button or press Enter to get a response
3. Toggle "Graph Mode" to switch to the graph visualization
4. Explore the knowledge graph built from your conversations
5. Use the tools in Graph Mode to interact with nodes

## Dependencies

- Flask: Web framework
- Flask-SQLAlchemy: ORM for database interactions
- Requests: For API calls
- scikit-learn: For text processing and similarity calculations
- Sigma.js: For graph visualization 