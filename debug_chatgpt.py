#!/usr/bin/env python3
"""
Debug script to examine ChatGPT page structure in headless mode
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

def debug_chatgpt_page():
    """Debug ChatGPT page structure"""
    driver = None
    try:
        print("🔧 Creating browser...")
        driver = create_headless_browser()
        
        print("🌐 Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Wait for initial load
        time.sleep(10)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check for cookie/consent dialogs
        print("\n🍪 Checking for cookie/consent dialogs...")
        cookie_selectors = [
            'button[id*="accept"]',
            'button[class*="accept"]',
            'button[aria-label*="Accept"]',
            'button:contains("Accept")',
            'button:contains("Allow")',
            '[data-testid*="accept"]'
        ]
        
        for selector in cookie_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"🎯 Found cookie button: {selector}")
                    elements[0].click()
                    time.sleep(2)
                    break
            except:
                continue
        
        # Look for input elements
        print("\n🔍 Looking for input elements...")
        input_selectors = [
            'textarea[data-testid="prompt-textarea"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="message"]',
            'textarea',
            'input[type="text"]'
        ]
        
        found_input = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Found input: {selector}")
                        found_input = element
                        break
                if found_input:
                    break
            except:
                continue
        
        if found_input:
            print("\n📝 Testing message sending...")
            try:
                found_input.click()
                time.sleep(0.5)
                found_input.clear()
                found_input.send_keys("Hello, what is 1+1?")
                time.sleep(1)
                found_input.send_keys(Keys.RETURN)
                print("✅ Message sent!")
                
                # Wait a bit for response to start
                time.sleep(10)
                
                # Look for response containers
                print("\n🔍 Looking for response containers...")
                
                # Get page source to analyze
                page_source = driver.page_source
                
                # Look for common response patterns
                response_indicators = [
                    'data-message-author-role="assistant"',
                    'data-message-role="assistant"',
                    'data-testid="conversation"',
                    'class="prose"',
                    'class="markdown"'
                ]
                
                for indicator in response_indicators:
                    if indicator in page_source:
                        print(f"📍 Found response indicator in HTML: {indicator}")
                
                # Try to find actual response elements
                response_selectors = [
                    'div[data-message-author-role="assistant"]',
                    'div[data-message-role="assistant"]',
                    '[data-message-author-role="assistant"]',
                    '.prose',
                    '.markdown',
                    'div:contains("1+1")',
                    'div:contains("2")',
                    'div:contains("=")'
                ]
                
                for selector in response_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"🎯 Found response elements with {selector}: {len(elements)} found")
                            for i, element in enumerate(elements[-3:]):  # Last 3 elements
                                try:
                                    text = element.text.strip()
                                    if text:
                                        print(f"  📝 Element {i}: {text[:200]}...")
                                except:
                                    pass
                    except:
                        continue
                
            except Exception as e:
                print(f"❌ Error testing message: {e}")
        
        else:
            print("❌ No input element found")
            
        # Save page source for analysis
        try:
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("💾 Page source saved to debug_page_source.html")
        except Exception as e:
            print(f"⚠️ Could not save page source: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
                print("🧹 Browser closed")
            except:
                pass
        cleanup_thread_resources()

if __name__ == "__main__":
    debug_chatgpt_page()
