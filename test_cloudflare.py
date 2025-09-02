#!/usr/bin/env python3
"""
Test script to check Cloudflare bypass in headless mode
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script import setup_undetected_browser_parallel
import time
from selenium.webdriver.common.by import By

def test_cloudflare_bypass():
    """Test if we can bypass Cloudflare in headless mode"""
    print("🧪 Testing Cloudflare bypass in headless mode...")
    
    driver = None
    try:
        # Create headless browser
        print("📱 Creating headless browser...")
        driver = setup_undetected_browser_parallel(headless=True)
        print("✅ Browser created successfully!")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Check title immediately
        initial_title = driver.title
        print(f"📄 Initial title: {initial_title}")
        
        # Wait for Cloudflare challenge to complete
        max_wait = 60  # 1 minute
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            current_title = driver.title.lower()
            current_url = driver.current_url
            
            print(f"⏱️ {int(time.time() - start_time)}s - Title: {current_title}")
            
            # Check if we're past Cloudflare
            if "just a moment" not in current_title and "checking your browser" not in current_title:
                if "chatgpt" in current_title or "openai" in current_title:
                    print("✅ Successfully bypassed Cloudflare!")
                    
                    # Look for input elements
                    selectors = [
                        'textarea[data-testid="prompt-textarea"]',
                        'div[contenteditable="true"]',
                        'textarea[placeholder*="Message"]',
                        'textarea'
                    ]
                    
                    found_input = False
                    for selector in selectors:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"🎯 Found input element: {selector}")
                            found_input = True
                            break
                    
                    if found_input:
                        print("✅ ChatGPT is ready for interaction!")
                        return True
                    else:
                        print("⚠️ ChatGPT loaded but no input element found")
                        break
            
            time.sleep(5)
        
        print("❌ Failed to bypass Cloudflare or find input elements")
        print(f"Final URL: {driver.current_url}")
        print(f"Final title: {driver.title}")
        
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
    success = test_cloudflare_bypass()
    if success:
        print("\n🎉 Cloudflare bypass test passed!")
        print("Your automation should work!")
    else:
        print("\n💥 Cloudflare bypass test failed!")
        print("ChatGPT may be blocking headless browsers.")
    
    sys.exit(0 if success else 1)
