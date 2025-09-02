#!/usr/bin/env python3
"""
Simple test to check ChatGPT page access in headless mode
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script import setup_undetected_browser_parallel
import time
from selenium.webdriver.common.by import By

def test_chatgpt_access():
    """Test if we can access ChatGPT page in headless mode"""
    print("🧪 Testing ChatGPT page access in headless mode...")
    
    driver = None
    try:
        # Create headless browser
        print("📱 Creating headless browser...")
        driver = setup_undetected_browser_parallel(headless=True)
        print("✅ Browser created successfully!")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Wait for page to load
        time.sleep(10)
        
        # Check page title
        title = driver.title
        print(f"📄 Page title: {title}")
        
        # Check for common elements
        selectors_to_check = [
            'textarea',
            'div[contenteditable="true"]',
            'input',
            'main',
            'body'
        ]
        
        found_elements = []
        for selector in selectors_to_check:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    found_elements.append(f"{selector} ({len(elements)} found)")
            except Exception as e:
                pass
        
        print("🔍 Elements found:")
        for element in found_elements:
            print(f"  - {element}")
        
        # Get page source length
        page_source_length = len(driver.page_source)
        print(f"📊 Page source length: {page_source_length} characters")
        
        # Check if we got blocked or redirected
        current_url = driver.current_url
        print(f"🔗 Current URL: {current_url}")
        
        if page_source_length > 1000 and "chatgpt" in current_url.lower():
            print("✅ ChatGPT page access successful!")
            return True
        else:
            print("❌ ChatGPT page access may have issues!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("🧹 Browser closed")
            except Exception as e:
                print(f"⚠️ Browser cleanup warning: {e}")

if __name__ == "__main__":
    success = test_chatgpt_access()
    if success:
        print("\n🎉 ChatGPT access test passed!")
    else:
        print("\n💥 ChatGPT access test failed!")
    
    sys.exit(0 if success else 1)
