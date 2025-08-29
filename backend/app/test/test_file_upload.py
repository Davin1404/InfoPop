#!/usr/bin/env python3
"""
Test script to verify file upload functionality
"""
import requests
import json

def test_file_upload():
    """Test file upload endpoint"""
    print("🔍 Testing File Upload Functionality")
    print("=" * 50)
    
    # Create a simple test file
    test_content = "This is a test document for uploading to the knowledge base."
    
    # Test the upload endpoint
    url = "http://localhost:8001/upload-documents"
    
    files = {
        'file': ('test_upload.txt', test_content, 'text/plain')
    }
    
    try:
        print("📁 Uploading test file...")
        response = requests.post(url, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload successful!")
            print(f"   File ID: {result.get('file_id')}")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Message: {result.get('message')}")
            return result.get('file_id')
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ File upload error: {e}")
        return None

def test_list_documents():
    """Test listing uploaded documents"""
    print("\n📋 Testing document listing...")
    
    url = "http://localhost:8001/documents"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Document listing successful! Found {len(documents)} documents")
            for doc in documents:
                print(f"   - {doc.get('filename')} (ID: {doc.get('id')})")
            return documents
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Document listing error: {e}")
        return []

def test_delete_document(file_id):
    """Test deleting a document"""
    if not file_id:
        return
        
    print(f"\n🗑️ Testing document deletion (ID: {file_id})...")
    
    url = f"http://localhost:8001/documents/{file_id}"
    
    try:
        response = requests.delete(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document deletion successful!")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Document deletion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Document deletion error: {e}")

if __name__ == "__main__":
    # Test the complete flow
    file_id = test_file_upload()
    test_list_documents()
    test_delete_document(file_id)
    
    print("\n" + "=" * 50)
    print("File upload tests completed!")
