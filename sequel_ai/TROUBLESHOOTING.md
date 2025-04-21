# Troubleshooting Guide

## OpenRouter API Issues

### 404 Client Error: Not Found

If you see an error like `Error processing request: 404 Client Error: Not Found for url: https://openrouter.ai/api/v1/chat/completions`, it could be due to one of these issues:

1. **Invalid API Key**: Ensure your OpenRouter API key is valid and properly configured in the `.env` file.

2. **Model Availability**: The model `google/gemini-2.5-pro-exp-03-25:free` might no longer be available or has been renamed. Check the [OpenRouter models page](https://openrouter.ai/models) for currently available models.

3. **Missing Required Headers**: OpenRouter requires certain HTTP headers like `HTTP-Referer` for billing purposes. The application should include these, but you may need to verify.

To fix this, try the following:

1. **Update your API key**:
   - Get a valid API key from [OpenRouter](https://openrouter.ai/)
   - Update the `.env` file with your new key:
     ```
     OPENROUTER_API_KEY=your_new_api_key_here
     ```

2. **Try a different model**:
   - Check available models on OpenRouter
   - Edit `services/chat_service.py` and change the model name
   - For example:
     ```python
     data = {
         "model": "google/gemini-1.5-pro", # Or another available model
         "messages": [
             {"role": "user", "content": message}
         ]
     }
     ```

## Database Issues

If you encounter database errors:

1. **Delete the existing database**:
   - Remove the `instance/sequel_ai.db` file
   - Restart the application to create a fresh database

2. **Migration issues**:
   - If your database schema has changed, you may need to run migrations
   - For simple cases, just delete the database file and restart

## Installation Problems

If you have issues with Python dependencies:

1. **Upgrade pip**:
   ```
   pip install --upgrade pip
   ```

2. **Install dependencies in verbose mode**:
   ```
   pip install -v -r requirements.txt
   ```

3. **Virtual environment issues**:
   - If your virtual environment is corrupted, delete the `venv` folder
   - Create a new one using:
     ```bash
     # Windows
     python -m venv venv
     
     # Unix/Mac
     python3 -m venv venv
     ```

## Runtime Errors

If the application crashes or behaves unexpectedly:

1. **Check the console logs** for detailed error messages

2. **Turn on debug mode** by setting in `.env`:
   ```
   FLASK_ENV=development
   ```

3. **Verify module imports** - ensure all required modules are installed:
   ```
   pip install -r requirements.txt
   ```

## Getting Help

If you continue to have issues, please create an issue on the GitHub repository with:
- A detailed description of the problem
- Steps to reproduce
- Error messages and logs
- Your environment details (OS, Python version, etc.) 