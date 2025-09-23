# Fix for JWT Authentication Issue

The issue you're experiencing is that the JWT token is being rejected because the SECRET_KEY in your .env file is set to a placeholder value: `your_very_secure_secret_key_here`.

## Solution 1: Use Supabase Token Instead

I've updated the `document_upload_troubleshooter.py` script to use the Supabase token instead of the custom JWT token. The script now looks for the "supabase_token" in the login response first, and only falls back to "access_token" if the supabase token isn't found.

## Solution 2: Set a Proper SECRET_KEY

Alternatively, you should update the SECRET_KEY in your .env file to a proper secure value. Here's how:

1. Open your backend/.env file
2. Find this line:
   ```
   SECRET_KEY=your_very_secure_secret_key_here
   ```
3. Replace it with a secure random key:
   ```
   SECRET_KEY=gwbJY6p2LQkWVvZCFYqI53PsZI0tRYG9kOYXVe6R9Tk
   ```

You can generate a secure key using Python with:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Understanding the Issue

When you log in, the API creates a custom JWT token using the SECRET_KEY defined in your .env file. When validating this token for subsequent requests, it tries to verify the token signature using the same SECRET_KEY.

If the SECRET_KEY has been changed between token generation and verification, or if it's not properly set in the first place, the token validation will fail with the error:
`invalid JWT: unable to parse or verify signature, token signature is invalid: signature is invalid`

## Additional Troubleshooting

If you're still having issues after implementing one of the solutions above, make sure:

1. Your FastAPI server has restarted after changing the .env file (the SECRET_KEY is loaded at startup)
2. Check that your Supabase URL and keys are still valid
3. Ensure the user you're logging in with exists in the Supabase auth system
