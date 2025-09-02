#!/usr/bin/env python3
"""
FIXED ChatGPT automation script for TRUE parallelism
Solves the Chrome driver file locking issue
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import tempfile
import os
import threading
import logging
import uuid
import pyperclip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global settings
HEADLESS_MODE = True

# Thread-local storage
thread_local = threading.local()

# Global lock for Chrome driver creation - this fixes the file conflict!
chrome_creation_lock = threading.Lock()

def cleanup_thread_resources():
    """Clean up temporary directories created by this thread"""
    if hasattr(thread_local, 'temp_dirs'):
        import shutil
        for temp_dir in thread_local.temp_dirs:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        thread_local.temp_dirs = []

def create_headless_browser():
    """Create a headless browser with file conflict prevention"""
    thread_id = threading.get_ident()
    logger.info(f"🔧 Thread {thread_id}: Creating headless browser...")
    
    # CRITICAL: Use global lock to prevent file conflicts
    with chrome_creation_lock:
        try:
            # Create unique temporary directory for each thread
            unique_id = f"chrome_{thread_id}_{uuid.uuid4().hex[:8]}"
            temp_dir = tempfile.mkdtemp(prefix=unique_id)
            user_data_dir = os.path.join(temp_dir, "user_data")
            os.makedirs(user_data_dir, exist_ok=True)
            
            # Optimized Chrome options (compatible with undetected_chromedriver)
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            
            # User agent
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Small random delay to prevent simultaneous driver creation
            time.sleep(random.uniform(0.05, 0.15))  # Reduced from 0.1-0.3
            
            # Create driver with unique binary location
            driver = uc.Chrome(
                options=options,
                version_main=None,
                use_subprocess=False,
                driver_executable_path=None  # Let it auto-download to avoid conflicts
            )
            
            # Set faster timeouts for speed
            driver.set_page_load_timeout(25)  # Reduced from 45
            driver.implicitly_wait(5)  # Reduced from 8
            
            # Hide automation properties
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Store temp dir for cleanup
            if not hasattr(thread_local, 'temp_dirs'):
                thread_local.temp_dirs = []
            thread_local.temp_dirs.append(temp_dir)
            
            logger.info(f"✅ Thread {thread_id}: Browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Thread {thread_id}: Failed to create browser: {e}")
            if 'temp_dir' in locals():
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            raise
            user_data_dir = os.path.join(temp_dir, "user_data")
            os.makedirs(user_data_dir, exist_ok=True)
            
            # Simple and reliable options
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # User agent
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Small delay
            time.sleep(random.uniform(0.5, 1.5))
            
            # Create driver
            driver = uc.Chrome(
                options=options,
                version_main=None,
                use_subprocess=False
            )
            
            # Set timeouts
            driver.set_page_load_timeout(60)
            driver.implicitly_wait(10)
            
            # Store temp dir for cleanup
            if not hasattr(thread_local, 'temp_dirs'):
                thread_local.temp_dirs = []
            thread_local.temp_dirs.append(temp_dir)
            
            logger.info(f"✅ Thread {thread_id}: Browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Thread {thread_id}: Failed to create browser: {e}")
            if 'temp_dir' in locals():
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            raise

def wait_for_chatgpt_ready(driver, timeout=90):
    """Wait for ChatGPT to be ready for input"""
    thread_id = threading.get_ident()
    logger.info(f"⏳ Thread {thread_id}: Waiting for ChatGPT to be ready...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Check title
            title = driver.title.lower()
            
            # Handle Cloudflare
            if "just a moment" in title or "checking your browser" in title:
                logger.info(f"🛡️ Thread {thread_id}: Waiting for Cloudflare...")
                time.sleep(5)
                continue
            
            # Look for input elements - Updated selectors
            selectors = [
                'textarea[data-id="root"]',  # Current ChatGPT main input
                'div[contenteditable="true"][data-id="root"]',  # Alternative contenteditable
                'textarea[placeholder*="Message"]',  # Generic message input
                'div[contenteditable="true"]',  # Generic contenteditable
                'textarea[data-testid="prompt-textarea"]',  # Old selector
                'textarea',  # Fallback
                '#prompt-textarea'  # ID-based selector
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✅ Thread {thread_id}: ChatGPT ready - found {selector}")
                            return element
                except:
                    continue
            
            time.sleep(3)
            
        except Exception as e:
            logger.warning(f"⚠️ Thread {thread_id}: Error checking readiness: {e}")
            time.sleep(3)
    
    logger.error(f"❌ Thread {thread_id}: ChatGPT not ready after {timeout}s")
    return None

def send_message(driver, input_element, message):
    """Send message to ChatGPT"""
    thread_id = threading.get_ident()
    logger.info(f"📝 Thread {thread_id}: Sending message...")
    
    try:
        # Click and focus
        input_element.click()
        time.sleep(0.5)
        
        # Clear and type
        input_element.clear()
        time.sleep(0.3)
        
        # Use clipboard for faster typing
        pyperclip.copy(message)
        input_element.send_keys(Keys.CONTROL + 'v')
        time.sleep(1)
        
        # Send
        input_element.send_keys(Keys.RETURN)
        
        logger.info(f"✅ Thread {thread_id}: Message sent")
        return True
        
    except Exception as e:
        logger.error(f"❌ Thread {thread_id}: Failed to send message: {e}")
        return False

def wait_for_response(driver, timeout=60):
    """Wait for ChatGPT response using the proven debug method"""
    thread_id = threading.get_ident()
    logger.info(f"⏳ Thread {thread_id}: Waiting for response...")
    
    # Wait for response to generate (same as debug script)
    time.sleep(10)
    
    # Try the updated selectors for current ChatGPT interface
    selectors = [
        'div[data-message-author-role="assistant"] .markdown',  # Assistant message with markdown
        'div[data-message-author-role="assistant"]',
        '[data-message-author-role="assistant"]',
        '.markdown',
        '.prose',
        'div[class*="markdown"]',
        'div[class*="prose"]',
        'article',
        'div[data-testid*="conversation-turn"]'
    ]
    
    try:
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"🎯 Found response elements with {selector}: {len(elements)} found")
                    response_text = elements[-1].text.strip()
                    if response_text and len(response_text) > 5:
                        logger.info(f"✅ Thread {thread_id}: Response found: {response_text[:100]}...")
                        return response_text
            except Exception as e:
                logger.warning(f"⚠️ Thread {thread_id}: Error with selector {selector}: {e}")
                continue
    except Exception as e:
        logger.error(f"❌ Thread {thread_id}: Error finding response: {e}")
    
    logger.error(f"❌ Thread {thread_id}: No response found")
    return None

def get_chatgpt_response(question):
    """Main function to get ChatGPT response - working version"""
    thread_id = threading.get_ident()
    logger.info(f"🚀 Thread {thread_id}: Starting ChatGPT query...")
    
    driver = None
    try:
        # Create browser
        driver = create_headless_browser()
        
        # OPTIMIZED: Direct auth page visit with minimal wait times
        logger.info(f"🌐 Thread {thread_id}: Pre-loading auth page...")
        driver.get("https://auth.openai.com")
        time.sleep(1.5)  # Reduced from 3s
        
        # Navigate directly to ChatGPT with minimal wait
        logger.info(f"🌐 Thread {thread_id}: Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        time.sleep(2)  # Reduced from 5s
        
        current_url = driver.current_url
        logger.info(f"🔗 Thread {thread_id}: Current URL: {current_url}")
        
        # Quick fallback if needed
        if "auth.openai.com" in current_url:
            logger.info(f"🔐 Thread {thread_id}: Trying direct chat URL...")
            driver.get("https://chatgpt.com/chat")
            time.sleep(1.5)  # Reduced from 3s
            current_url = driver.current_url
        
        logger.info(f"✅ Thread {thread_id}: ChatGPT loaded")
        
        # OPTIMIZED: Quick element detection (no extensive scraping)
        logger.info(f"� Thread {thread_id}: Finding input element...")
        
        # Fast input detection with proven selectors
        input_selectors = [
            '#prompt-textarea',  # Main target
            'div.ProseMirror',   # ProseMirror editor
            'textarea[placeholder*="Ask anything"]',  # Fallback
            'div[contenteditable="true"]'  # Generic contenteditable
        ]
        
        found_input = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        found_input = element
                        logger.info(f"✅ Thread {thread_id}: Found input element")
                        break
                if found_input:
                    break
            except:
                continue
        
        if not found_input:
            logger.error(f"❌ Thread {thread_id}: No input element found")
            return f"Thread {thread_id}: No input element found"
        
        # OPTIMIZED: Fast message sending
        logger.info(f"📝 Thread {thread_id}: Sending message...")
        found_input.click()
        time.sleep(0.2)  # Reduced from 0.5s
        found_input.clear()
        found_input.send_keys(question)
        time.sleep(0.5)  # Reduced from 1s
        found_input.send_keys(Keys.RETURN)
        logger.info(f"✅ Thread {thread_id}: Message sent")
        
        # OPTIMIZED: Faster response detection
        logger.info(f"⏳ Thread {thread_id}: Waiting for response...")
        
        # Reduced wait time and check more frequently
        max_wait = 15  # Reduced from longer waits
        check_interval = 1
        waited = 0
        
        while waited < max_wait:
            time.sleep(check_interval)
            waited += check_interval
            
            # Quick response check with primary selector
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-message-author-role="assistant"] .markdown')
                if elements:
                    response_text = elements[-1].text.strip()
                    if response_text and len(response_text) > 10:  # Ensure substantial response
                        logger.info(f"✅ Thread {thread_id}: Response found in {waited}s: {response_text[:100]}...")
                        return response_text
            except:
                pass
        
        # Fallback: try other selectors if primary didn't work
        response_selectors = [
            'div[data-message-author-role="assistant"]',
            '[data-message-author-role="assistant"]',
            '.markdown',
            '.prose'
        ]
        
        for selector in response_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    response_text = elements[-1].text.strip()
                    if response_text and len(response_text) > 10:
                        logger.info(f"✅ Thread {thread_id}: Response found with fallback: {response_text[:100]}...")
                        return response_text
            except:
                continue
        
        return f"Thread {thread_id}: No response found"
        
    except Exception as e:
        error_msg = f"Thread {thread_id}: Error - {str(e)}"
        logger.error(error_msg)
        return error_msg
        
    finally:
        if driver:
            try:
                driver.quit()
                logger.info(f"🧹 Thread {thread_id}: Browser closed")
            except Exception as e:
                logger.warning(f"⚠️ Thread {thread_id}: Cleanup warning: {e}")
        
        cleanup_thread_resources()

# For backward compatibility
setup_undetected_browser_parallel = create_headless_browser
automated_chatgpt_query = lambda x: get_chatgpt_response(f"Test query {x}")

if __name__ == "__main__":
    # Test the simplified version
    response = get_chatgpt_response("What is 2+2? Give a short answer.")
    print(f"Response: {response}")
