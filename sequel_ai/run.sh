#!/bin/bash

echo "Starting Sequel AI..."

# Activate virtual environment
source venv/bin/activate

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application
flask run 