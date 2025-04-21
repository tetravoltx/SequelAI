import requests
import json
import os
from flask import current_app
from models.db_model import db, Chat, Node, Edge
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# You'll need to provide your OpenRouter API key
# OPENROUTER_API_KEY = "your_api_key_here"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def process_chat(message):
    """Process a chat message using OpenRouter API with Gemini model"""
    
    # Check if API key is set
    if not OPENROUTER_API_KEY:
        # For development/testing, return a mock response
        response = f"Mock response to: {message} (Please set OPENROUTER_API_KEY environment variable)"
    else:
        # Make request to OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "google/gemini-2.5-pro-exp-03-25:free",
            "messages": [
                {"role": "user", "content": message}
            ]
        }
        
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=data)
            resp.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse response
            response_data = resp.json()
            response = response_data["choices"][0]["message"]["content"]
        except Exception as e:
            response = f"Error processing request: {str(e)}"
    
    # Store the chat in the database
    chat = Chat(message=message, response=response)
    db.session.add(chat)
    db.session.commit()
    
    return response

def extract_concepts(message, response):
    """Extract key concepts from the conversation and build the knowledge graph"""
    
    # Combine message and response for concept extraction
    combined_text = message + " " + response
    
    # Simple approach: extract nouns and noun phrases using regex
    # In a production system, you'd want to use a proper NLP library like spaCy
    noun_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'  # Matches capitalized words/phrases
    concepts = re.findall(noun_pattern, combined_text)
    
    # Filter out common non-concept words
    stop_words = ["I", "You", "He", "She", "It", "We", "They", "This", "That", "These", "Those"]
    concepts = [c for c in concepts if c not in stop_words]
    
    # Remove duplicates while preserving order
    unique_concepts = []
    for concept in concepts:
        if concept not in unique_concepts:
            unique_concepts.append(concept)
    
    # Limit to the most significant concepts (top 5)
    top_concepts = unique_concepts[:5] if len(unique_concepts) > 5 else unique_concepts
    
    # Skip if no concepts found
    if not top_concepts:
        return
    
    # Add nodes for each concept
    nodes = []
    for concept in top_concepts:
        # Check if node already exists
        existing_node = Node.query.filter(Node.label == concept).first()
        
        if existing_node:
            nodes.append(existing_node)
        else:
            # Create a new node
            node = Node(label=concept)
            db.session.add(node)
            db.session.flush()  # Flush to get the ID without committing
            nodes.append(node)
    
    # Create edges between related concepts
    if len(nodes) > 1:
        # Calculate similarity between concept pairs using TF-IDF and cosine similarity
        vectorizer = TfidfVectorizer()
        concept_labels = [node.label for node in nodes]
        tfidf_matrix = vectorizer.fit_transform(concept_labels)
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Create edges for related concepts (similarity > 0.1)
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                similarity = cosine_sim[i][j]
                if similarity > 0.1:  # Threshold for creating an edge
                    # Check if edge already exists
                    existing_edge = Edge.query.filter(
                        ((Edge.source_id == nodes[i].id) & (Edge.target_id == nodes[j].id)) |
                        ((Edge.source_id == nodes[j].id) & (Edge.target_id == nodes[i].id))
                    ).first()
                    
                    if not existing_edge:
                        edge = Edge(
                            source_id=nodes[i].id,
                            target_id=nodes[j].id,
                            weight=float(similarity)
                        )
                        db.session.add(edge)
    
    # Commit all changes
    db.session.commit() 