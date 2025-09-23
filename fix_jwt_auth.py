"""
Reset JWT Secret Key

This script fixes the JWT authentication by:
1. Setting a consistent SECRET_KEY in the .env file
2. Providing instructions to restart the server
"""
import os
import sys

def reset_secret_key():
    """Reset the SECRET_KEY in .env file"""
    # Path to .env file
    env_file = os.path.join(os.path.dirname(__file__), "backend", ".env")
    
    if not os.path.exists(env_file):
        print(f"❌ Error: .env file not found at {env_file}")
        return False
    
    # The known working secret key
    secret_key = "bvKmIR-A0kWrSvZaqaZ9c5XDUy8AkXsG5x1GG2vYJ7I"
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the SECRET_KEY line
    for i, line in enumerate(lines):
        if line.startswith("SECRET_KEY="):
            lines[i] = f"SECRET_KEY={secret_key}\n"
            break
    
    # Write the updated content
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated SECRET_KEY in {env_file}")
    return True

def create_jwt_fix_file():
    """Create a temporary fix file to bypass JWT verification"""
    fix_file = os.path.join(os.path.dirname(__file__), "backend", "jwt_fix.py")
    
    content = """# JWT Temporary Fix
# This file needs to be imported at the start of your FastAPI app

import os
import sys

# Set the correct SECRET_KEY environment variable
os.environ["SECRET_KEY"] = "bvKmIR-A0kWrSvZaqaZ9c5XDUy8AkXsG5x1GG2vYJ7I"

# Print diagnostic info
print(f"JWT Fix applied with SECRET_KEY={os.environ['SECRET_KEY']}")
"""
    
    with open(fix_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created JWT fix file: {fix_file}")
    return True

def print_instructions():
    """Print instructions for completing the fix"""
    print("\n=== JWT Authentication Fix Instructions ===\n")
    print("1. In your backend/main.py file, add this import at the very top:")
    print("   import jwt_fix\n")
    print("2. Restart your FastAPI server with:")
    print("   cd backend")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload\n")
    print("3. Test the authentication with:")
    print("   python test_jwt_auth.py\n")
    print("If you're still having issues, try:")
    print("1. Stop the server")
    print("2. Clear any cached Python files (*.pyc)")
    print("3. Restart the server with:")
    print("   cd backend")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")

def main():
    """Execute the fix"""
    print("=== Fixing JWT Authentication ===\n")
    
    # Reset SECRET_KEY in .env
    if reset_secret_key():
        print("Step 1: SECRET_KEY updated in .env file")
    else:
        print("❌ Failed to update SECRET_KEY")
        return
    
    # Create JWT fix file
    if create_jwt_fix_file():
        print("Step 2: JWT fix file created")
    else:
        print("❌ Failed to create JWT fix file")
        return
    
    # Print instructions
    print_instructions()

if __name__ == "__main__":
    main()