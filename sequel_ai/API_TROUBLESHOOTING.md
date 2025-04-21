# OpenRouter API Troubleshooting

## Current Issue: Model Access Restrictions

We encountered an error with the `google/gemini-2.5-pro-exp-03-25:free` model:

```
Error processing request: API Error (Status 404): {"error":{"message":"Usage of the experimental google/gemini-2.5-pro-exp-03-25 model has been limited to OpenRouter users who have purchased at least 10 credits ever. Please consider using the paid version at https://openrouter.ai/google/gemini-2.5-pro-preview-03-25 or adding your own API keys in https://openrouter.ai/settings/integrations","code":404}}
```

### Solution

We've updated the application to use `openai/gpt-3.5-turbo` which is a free model available without credit restrictions.

## Testing the API Connection

1. Start the application: 
   ```
   python app.py
   ```

2. Visit the debug endpoint in your browser:
   ```
   http://localhost:5000/debug/api_test
   ```

   This will display detailed information about the API request and response.

## Available Free Models

If you want to try a different model, here are some free options available on OpenRouter:

- `openai/gpt-3.5-turbo`
- `anthropic/claude-instant-1.2`
- `google/palm-2-chat-bison`
- `mistralai/mistral-7b-instruct`

To change the model, edit the `.env` file and update the `MODEL` variable.

## API Key Issues

If you're experiencing issues with the API key:

1. Create a free account on [OpenRouter](https://openrouter.ai/)
2. Generate a new API key in your dashboard
3. Update the `.env` file with your new key:
   ```
   OPENROUTER_API_KEY=your-new-key-here
   ```

## Request Format Issues

If you're getting 400 Bad Request errors, ensure your request format is correct:

1. The request should have a valid `model` parameter
2. The `messages` array should contain at least one message with `role` and `content`
3. The `role` should be one of: "user", "assistant", or "system"

## References

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Available Models](https://openrouter.ai/models)
- [API Reference](https://openrouter.ai/docs/api-reference) 