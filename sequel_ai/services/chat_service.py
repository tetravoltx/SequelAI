import requests
import json
import os
import time
from flask import current_app, request
from models.db_model import db, Chat, Node, Edge
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Get the OpenRouter API key and model from environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = os.environ.get("MODEL", "openai/gpt-3.5-turbo")  # Changed default model to gpt-3.5-turbo
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def process_chat(message, max_retries=3):
    """Process a chat message using OpenRouter API"""
    
    # Check if API key is set
    if not OPENROUTER_API_KEY:
        # For development/testing, return a mock response
        print("Warning: OPENROUTER_API_KEY is not set. Using mock response.")
        response = f"Mock response to: {message} (Please set OPENROUTER_API_KEY environment variable)"
    else:
        # Make request to OpenRouter API with proper headers
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Sequel AI"
        }
        
        # Simplified request format following OpenRouter documentation
        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500  # Reduced token limit to ensure we're within free tier limits
        }
        
        # Initialize response
        response = None
        retries = 0
        
        while retries < max_retries:
            try:
                print(f"Making request to OpenRouter API: {OPENROUTER_URL}")
                print(f"Using model: {MODEL}")
                print(f"API Key (first 5 chars): {OPENROUTER_API_KEY[:5]}...")
                print(f"Request data: {json.dumps(data)}")
                
                # Make the API request
                resp = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
                
                # Print response details for debugging
                print(f"Response status: {resp.status_code}")
                print(f"Response body: {resp.text[:300]}")
                
                if resp.status_code == 200:
                    # Parse successful response
                    response_data = resp.json()
                    
                    # Extract content from choices[0].message.content
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        choice = response_data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            response = choice["message"]["content"]
                            print(f"Successfully received response: {response[:100]}...")
                            break  # Success, exit the retry loop
                        else:
                            print("Warning: Unexpected response format - missing message.content")
                            response = "Error: Unexpected response format from API"
                            break
                    else:
                        print("Warning: No choices in API response")
                        response = "Error: No response content from API"
                        break
                    
                elif resp.status_code == 400:
                    # Handle bad request errors
                    error_data = resp.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    print(f"Bad request error: {error_message}")
                    response = f"API Error (400 Bad Request): {error_message}"
                    break
                    
                elif resp.status_code == 404:
                    # Handle model not found
                    error_data = resp.json()
                    error_message = error_data.get("error", {}).get("message", "Model not found or unavailable")
                    print(f"Model not found error: {error_message}")
                    response = f"API Error: {error_message}"
                    break
                    
                elif resp.status_code == 429:  # Rate limit exceeded
                    print("Rate limit exceeded, waiting before retry...")
                    time.sleep(5)  # Wait 5 seconds before retrying
                    retries += 1
                    
                else:
                    # Handle other errors
                    print(f"Error response body: {resp.text}")
                    error_msg = f"API Error (Status {resp.status_code}): {resp.text}"
                    response = f"Error processing request: {error_msg}"
                    break
                    
            except requests.exceptions.Timeout:
                print(f"Request timed out (attempt {retries+1}/{max_retries})")
                retries += 1
                time.sleep(2)  # Wait 2 seconds before retrying
                
            except Exception as e:
                print(f"Error in process_chat: {str(e)}")
                response = f"Error processing request: {str(e)}"
                break  # Exit on other errors
        
        # If all retries failed, provide a fallback response
        if response is None:
            response = "I'm sorry, but I couldn't process your request at this time. Please try again later."
    
    # Store the chat in the database
    chat = Chat(message=message, response=response)
    db.session.add(chat)
    db.session.commit()
    
    return response

def extract_concepts(message, response):
    """Extract key concepts from the conversation and build the knowledge graph"""
    
    # Skip concept extraction for error messages
    if response.startswith("Error processing request:") or response.startswith("I'm sorry") or response.startswith("API Error"):
        return
    
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