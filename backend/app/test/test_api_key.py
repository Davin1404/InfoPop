#!/usr/bin/env python3
"""
Test script to verify OpenAI API key validity
"""
import os
from dotenv import load_dotenv
import requests
import json

def test_openai_api_key():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"Testing API key: {api_key[:20]}...{api_key[-4:] if api_key else 'NOT_SET'}")
    
    if not api_key:
        print("❌ No API key found in environment variables")
        return False
    
    # Test with OpenAI's official API
    print("\n1. Testing with OpenAI official API (api.openai.com)...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoint: List models
    try:
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ OpenAI official API: Key is valid!")
            models = response.json()
            print(f"   Available models: {len(models.get('data', []))} models found")
            return True
        elif response.status_code == 401:
            print("❌ OpenAI official API: Invalid API key (401 Unauthorized)")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ OpenAI official API: Error {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAI official API: Network error - {e}")
    
    # Test with the proxy API from model_config.json
    print("\n2. Testing with proxy API (aihub.gz4399.com)...")
    
    try:
        response = requests.get(
            'https://aihub.gz4399.com/v1/models',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Proxy API: Key is valid!")
            models = response.json()
            print(f"   Available models: {len(models.get('data', []))} models found")
            
            # Check if gpt-4.1 exists
            model_names = [model['id'] for model in models.get('data', [])]
            if 'gpt-4.1' in model_names:
                print("✅ Model 'gpt-4.1' is available on proxy API")
            else:
                print("❌ Model 'gpt-4.1' is NOT available on proxy API")
                print(f"   Available models include: {model_names[:10]}...")
            
            return True
        elif response.status_code == 401:
            print("❌ Proxy API: Invalid API key (401 Unauthorized)")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ Proxy API: Error {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Proxy API: Network error - {e}")
    
    return False

def test_simple_chat():
    """Test a simple chat completion"""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        return
    
    print("\n3. Testing chat completion with gpt-3.5-turbo...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello! Just say 'Hi' back."}],
        "max_tokens": 10
    }
    
    # Test with proxy API
    try:
        response = requests.post(
            'https://aihub.gz4399.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ Chat test successful! Response: '{message}'")
        else:
            print(f"❌ Chat test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat test error: {e}")

if __name__ == "__main__":
    print("🔍 Testing OpenAI API Key Validity")
    print("=" * 50)
    
    test_openai_api_key()
    test_simple_chat()
    
    print("\n" + "=" * 50)
    print("Test completed!")
