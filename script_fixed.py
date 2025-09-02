#!/usr/bin/env python3
"""
FIXED ChatGPT automation script with stale element reference handling
Solves both Chrome driver file locking AND stale element issues
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time
import random
import tempfile
import os
import threading
import logging
import uuid

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
            time.sleep(random.uniform(0.05, 0.15))
            
            # Create driver with unique binary location
            driver = uc.Chrome(
                options=options,
                version_main=None,
                use_subprocess=False,
                driver_executable_path=None  # Let it auto-download to avoid conflicts
            )
            
            # Set faster timeouts for speed
            driver.set_page_load_timeout(25)
            driver.implicitly_wait(5)
            
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

def find_input_element(driver, max_attempts=3, wait_time=2):
    """Find input element with retry logic to handle dynamic content"""
    thread_id = threading.get_ident()
    
    input_selectors = [
        '#prompt-textarea',  # Main target
        'textarea[data-id="root"]',  # Updated ChatGPT selector
        'div[contenteditable="true"][data-id="root"]',  # Alternative contenteditable
        'div.ProseMirror',   # ProseMirror editor
        'textarea[placeholder*="Ask anything"]',  # Fallback
        'textarea[placeholder*="Message"]',  # Generic message input
        'div[contenteditable="true"]'  # Generic contenteditable
    ]
    
    for attempt in range(max_attempts):
        logger.info(f"🔍 Thread {thread_id}: Finding input element (attempt {attempt + 1})...")
        
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        logger.info(f"✅ Thread {thread_id}: Found input element with selector: {selector}")
                        return element
            except Exception as e:
                logger.debug(f"Debug: Selector {selector} failed: {e}")
                continue
        
        if attempt < max_attempts - 1:
            logger.info(f"⏳ Thread {thread_id}: Input not found, waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    logger.error(f"❌ Thread {thread_id}: No input element found after {max_attempts} attempts")
    return None

def send_message_robust(driver, message, max_retries=3):
    """Send message with robust stale element handling"""
    thread_id = threading.get_ident()
    
    for attempt in range(max_retries):
        try:
            # Find the input element (or re-find if stale)
            input_element = find_input_element(driver)
            if not input_element:
                logger.error(f"❌ Thread {thread_id}: Could not find input element")
                return False
            
            logger.info(f"📝 Thread {thread_id}: Sending message (attempt {attempt + 1})...")
            
            # Focus on the element using JavaScript for reliability
            driver.execute_script("arguments[0].focus();", input_element)
            time.sleep(0.3)
            
            # Clear existing content
            try:
                input_element.clear()
            except:
                # If clear() fails, try with JavaScript
                driver.execute_script("arguments[0].value = '';", input_element)
            time.sleep(0.2)
            
            # Type the message
            input_element.send_keys(message)
            time.sleep(0.5)
            
            # Send the message
            input_element.send_keys(Keys.RETURN)
            logger.info(f"✅ Thread {thread_id}: Message sent successfully")
            return True
            
        except StaleElementReferenceException as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️ Thread {thread_id}: Stale element detected, retrying in 1s...")
                time.sleep(1)
                continue
            else:
                logger.error(f"❌ Thread {thread_id}: Failed after {max_retries} attempts due to stale element")
                return False
        except Exception as e:
            logger.error(f"❌ Thread {thread_id}: Failed to send message: {e}")
            return False
    
    return False

def wait_for_response(driver, timeout=60):
    """Wait for ChatGPT response with robust element finding"""
    thread_id = threading.get_ident()
    logger.info(f"⏳ Thread {thread_id}: Waiting for response...")
    
    # Wait for response to start generating
    time.sleep(3)
    
    response_selectors = [
        'div[data-message-author-role="assistant"] .markdown',  # Primary target
        'div[data-message-author-role="assistant"]',
        '[data-message-author-role="assistant"]',
        '.markdown',
        '.prose'
    ]
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        for selector in response_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    response_text = elements[-1].text.strip()
                    if response_text and len(response_text) > 10:  # Ensure substantial response
                        logger.info(f"✅ Thread {thread_id}: Response found: {response_text[:100]}...")
                        return response_text
            except:
                continue
        
        time.sleep(2)  # Check every 2 seconds
    
    logger.error(f"❌ Thread {thread_id}: No response found after {timeout}s")
    return None

def get_chatgpt_response(question):
    """Main function to get ChatGPT response with stale element protection"""
    thread_id = threading.get_ident()
    logger.info(f"🚀 Thread {thread_id}: Starting ChatGPT query...")
    
    driver = None
    try:
        # Create browser
        driver = create_headless_browser()
        
        # Navigate to ChatGPT
        logger.info(f"🌐 Thread {thread_id}: Pre-loading auth page...")
        driver.get("https://auth.openai.com")
        time.sleep(1.5)
        
        logger.info(f"🌐 Thread {thread_id}: Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        time.sleep(2)
        
        current_url = driver.current_url
        logger.info(f"🔗 Thread {thread_id}: Current URL: {current_url}")
        
        # Quick fallback if needed
        if "auth.openai.com" in current_url:
            logger.info(f"🔐 Thread {thread_id}: Trying direct chat URL...")
            driver.get("https://chatgpt.com/chat")
            time.sleep(1.5)
            current_url = driver.current_url
        
        logger.info(f"✅ Thread {thread_id}: ChatGPT loaded")
        
        # Use robust message sending
        success = send_message_robust(driver, question)
        if not success:
            return f"Thread {thread_id}: Failed to send message"
        
        # Wait for response
        response = wait_for_response(driver)
        if response:
            return response
        else:
            return f"Thread {thread_id}: No response received"
        
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
    # Test the fixed version
    response = get_chatgpt_response("What is 2+2? Give a short answer.")
    print(f"Response: {response}")
