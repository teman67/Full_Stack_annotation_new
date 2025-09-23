"""
Comprehensive fix for document upload authentication issues
Applies all necessary patches to resolve user authentication and project access problems
"""
import os
import sys

def apply_auth_fix():
    """Apply comprehensive authentication and document upload fixes"""
    print("=== APPLYING COMPREHENSIVE AUTH AND DOCUMENT UPLOAD FIX ===")
    
    try:
        # Import the main app to modify it
        import importlib.util
        from pathlib import Path
        
        # Get the path to main.py
        main_path = Path(__file__).parent.parent / "main.py"
        
        if not main_path.exists():
            print(f"Warning: main.py not found at {main_path}")
            return False
        
        # Load and modify the FastAPI app at runtime
        print("Modifying FastAPI app to use fixed authentication and document upload...")
        
        # Replace the documents router with our fixed version
        from fastapi import FastAPI
        from app.api.documents_upload_fixed import router as fixed_documents_router
        
        # Find the app instance and replace the router
        import main
        app = main.app
        
        # Remove existing documents router
        print("Removing existing documents router...")
        for route in app.routes:
            if hasattr(route, 'path') and '/api/documents' in route.path:
                app.routes.remove(route)
        
        # Add our fixed router
        print("Adding fixed documents router...")
        app.include_router(fixed_documents_router, prefix="/api/documents", tags=["documents"])
        
        print("✅ Fixed authentication and document upload applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        import traceback
        traceback.print_exc()
        return False

# Apply the fix when this module is imported
if __name__ == "__main__" or True:  # Always apply when imported
    try:
        apply_auth_fix()
    except Exception as e:
        print(f"Warning: Could not apply comprehensive auth fix: {e}")