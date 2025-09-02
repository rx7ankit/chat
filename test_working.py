#!/usr/bin/env python3
"""
Working ChatGPT automation based on successful debug script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script_simple import create_headless_browser, cleanup_thread_resources
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chatgpt_response_working(question):
    """Working ChatGPT response function based on debug script"""
    thread_id = 1  # Simple thread ID
    
    driver = None
    try:
        print(f"🚀 Starting ChatGPT query: {question}")
        
        # Create browser
        driver = create_headless_browser()
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Wait for page load
        time.sleep(10)
        
        # Find input element
        print("🔍 Looking for input...")
        input_selectors = [
            'div[contenteditable="true"]',
            'textarea[data-testid="prompt-textarea"]',
            'textarea[placeholder*="Message"]',
            'textarea'
        ]
        
        found_input = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        found_input = element
                        print(f"✅ Found input: {selector}")
                        break
                if found_input:
                    break
            except:
                continue
        
        if not found_input:
            return "No input element found"
        
        # Send message
        print("📝 Sending message...")
        found_input.click()
        time.sleep(0.5)
        found_input.clear()
        found_input.send_keys(question)
        time.sleep(1)
        found_input.send_keys(Keys.RETURN)
        print("✅ Message sent!")
        
        # Wait for response (exactly like debug script)
        print("⏳ Waiting for response...")
        time.sleep(10)  # Same wait time as debug script
        
        # Look for response (same selectors as debug script)
        response_selectors = [
            'div[data-message-author-role="assistant"]',
            '[data-message-author-role="assistant"]',
            '.prose',
            '.markdown'
        ]
        
        for selector in response_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    response_text = elements[-1].text.strip()
                    if response_text and len(response_text) > 5:
                        print(f"✅ Found response: {response_text[:100]}...")
                        return response_text
            except:
                continue
        
        return "No response found"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Error: {str(e)}"
        
    finally:
        if driver:
            try:
                driver.quit()
                print("🧹 Browser closed")
            except:
                pass
        cleanup_thread_resources()

if __name__ == "__main__":
    # Test the working version
    response = get_chatgpt_response_working("What is 3+3? Give a short answer.")
    print(f"\n🎯 Final Response: {response}")
