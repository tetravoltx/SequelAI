@echo off
echo Starting Sequel AI...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Run the Flask application
flask run 