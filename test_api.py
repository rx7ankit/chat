#!/usr/bin/env python3
"""
Test script to verify the ChatGPT API endpoint works in headless mode
"""
import requests
import json
import time

def test_chatgpt_api():
    """Test the ChatGPT API endpoint"""
    print("🧪 Testing ChatGPT API with headless browser...")
    
    # API endpoint
    url = "http://127.0.0.1:8000/chat"
    
    # Test data
    test_data = {
        "question": "What is 2+2? Please give a very short answer."
    }
    
    print(f"📤 Sending request: {test_data['question']}")
    
    try:
        # Send POST request
        start_time = time.time()
        response = requests.post(url, json=test_data, timeout=120)  # 2 minute timeout
        end_time = time.time()
        
        print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Response: {result}")
            print("✅ API test passed!")
            return True
        else:
            print(f"❌ API test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ API test failed: Request timed out")
        return False
    except Exception as e:
        print(f"❌ API test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API test...")
    print("Make sure the FastAPI server is running on http://127.0.0.1:8000")
    print()
    
    success = test_chatgpt_api()
    
    if success:
        print("\n🎉 ChatGPT API test completed successfully!")
        print("Your headless automation is working correctly!")
    else:
        print("\n💥 ChatGPT API test failed!")
        print("Check the server logs for more details.")
