"""
Test script to verify the GET documents endpoint
"""
import requests
import json
from pathlib import Path

def test_get_documents_endpoint():
    print("=== TESTING GET DOCUMENTS ENDPOINT ===")
    
    # First check if the server is running
    try:
        response = requests.get("http://localhost:8000/api/documents/test", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Test endpoint response: {data}")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False
    
    # Check what documents exist in local storage
    print("\n=== CHECKING LOCAL DOCUMENT RECORDS ===")
    documents_dir = Path("local_document_records")
    if documents_dir.exists():
        json_files = list(documents_dir.glob("document_*.json"))
        print(f"Found {len(json_files)} local document files")
        
        project_1_docs = []
        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    doc_data = json.load(f)
                if doc_data.get("project_id") == 1:
                    project_1_docs.append(doc_data)
                    print(f"  - {doc_data.get('name')} (uploaded: {doc_data.get('created_at', 'unknown')})")
            except Exception as e:
                print(f"  - Error reading {json_file}: {e}")
        
        print(f"\nTotal documents for project 1: {len(project_1_docs)}")
        
        if project_1_docs:
            print("\nThe GET endpoint should return these documents.")
            print("If the frontend is not showing them, the issue might be:")
            print("1. Authentication token not being sent properly")
            print("2. Frontend not making the GET request")
            print("3. Frontend not displaying the response data")
            
            print("\nTo debug further:")
            print("1. Check browser developer tools Network tab")
            print("2. Look for GET request to /api/documents/project/1")
            print("3. Check if the request includes Authorization header")
            print("4. Verify the response contains the documents")
            
        return True
    else:
        print("❌ No local document records found")
        return False

if __name__ == "__main__":
    test_get_documents_endpoint()