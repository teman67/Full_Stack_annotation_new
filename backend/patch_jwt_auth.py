# Patch script for JWT authentication issues
import os
import sys
import secrets

def update_env_file():
    """Update the .env file with a secure SECRET_KEY"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        return False
    
    # Generate a secure random key
    new_secret_key = secrets.token_urlsafe(32)
    
    # Read the current .env file
    with open(env_path, 'r') as f:
        env_lines = f.readlines()
    
    # Update the SECRET_KEY line
    updated = False
    for i, line in enumerate(env_lines):
        if line.startswith('SECRET_KEY='):
            env_lines[i] = f'SECRET_KEY={new_secret_key}\n'
            updated = True
    
    # Write the updated .env file
    if updated:
        with open(env_path, 'w') as f:
            f.writelines(env_lines)
        print(f"✅ Updated SECRET_KEY in .env file to: {new_secret_key}")
    else:
        print("⚠️ SECRET_KEY line not found in .env file")
    
    return updated

def print_instructions():
    """Print instructions for applying the patch"""
    print("\n====== JWT Authentication Patch ======")
    print("\nThis script has updated your .env file with a new SECRET_KEY.")
    print("To complete the fix, you need to:")
    
    print("\n1. Restart your FastAPI server:")
    print("   cd backend")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n2. Try the authentication troubleshooter:")
    print("   python auth_troubleshooter.py")
    
    print("\n3. If issues persist, add DEBUG_AUTH=true to your environment:")
    print("   - Windows CMD: set DEBUG_AUTH=true")
    print("   - Windows PowerShell: $env:DEBUG_AUTH=\"true\"")
    print("   - Linux/macOS: export DEBUG_AUTH=true")
    
    print("\nThen restart the server with the debug flag:")
    print("python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug")

def main():
    """Main execution function"""
    print("Applying JWT authentication patch...")
    
    # Update .env file
    update_env_file()
    
    # Print instructions
    print_instructions()

if __name__ == "__main__":
    main()