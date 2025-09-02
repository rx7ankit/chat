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
            time.sleep(random.uniform(0.1, 0.3))
            
            # Create driver with unique binary location
            driver = uc.Chrome(
                options=options,
                version_main=None,
                use_subprocess=False,
                driver_executable_path=None  # Let it auto-download to avoid conflicts
            )
            
            # Set aggressive timeouts for speed
            driver.set_page_load_timeout(45)
            driver.implicitly_wait(8)
            
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
        
        # SOLUTION: Start by visiting the auth page directly, then navigate to ChatGPT
        logger.info(f"🌐 Thread {thread_id}: Pre-loading auth page to establish session...")
        driver.get("https://auth.openai.com")
        time.sleep(3)
        logger.info(f"✅ Thread {thread_id}: Auth page session established")
        
        # Now navigate directly to ChatGPT - this should avoid the redirect
        logger.info(f"🌐 Thread {thread_id}: Navigating to ChatGPT...")
        driver.get("https://chatgpt.com")
        time.sleep(5)  # Give more time for page load
        
        current_url = driver.current_url
        logger.info(f"🔗 Thread {thread_id}: Current URL after navigation: {current_url}")
        
        # Check if we're still on auth page (should be unlikely now)
        if "auth.openai.com" in current_url or "login" in current_url.lower():
            logger.info(f"🔐 Thread {thread_id}: Still on auth page, trying direct chat URL...")
            driver.get("https://chatgpt.com/chat")
            time.sleep(3)
            current_url = driver.current_url
            logger.info(f"🔗 Thread {thread_id}: Direct chat URL result: {current_url}")
        
        if "auth.openai.com" not in current_url and "login" not in current_url.lower():
            logger.info(f"✅ Thread {thread_id}: Successfully accessed ChatGPT without auth redirect")
        else:
            logger.info(f"⚠️ Thread {thread_id}: Still on auth page, will try to proceed anyway")
        
        # Wait for page load (same as working debug script)
        time.sleep(10)
        
        # Scrape and analyze the page content
        logger.info(f"🔍 Thread {thread_id}: Scraping page content for analysis...")
        
        # Get page title and URL
        title = driver.title
        current_url = driver.current_url
        logger.info(f"📄 Thread {thread_id}: Page title: {title}")
        logger.info(f"🔗 Thread {thread_id}: Current URL: {current_url}")
        
        # Get all input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        logger.info(f"📝 Thread {thread_id}: Found {len(inputs)} input elements")
        for i, inp in enumerate(inputs[:10]):  # Show first 10
            try:
                inp_type = inp.get_attribute("type") or "text"
                inp_placeholder = inp.get_attribute("placeholder") or ""
                inp_id = inp.get_attribute("id") or ""
                inp_class = inp.get_attribute("class") or ""
                logger.info(f"  Input {i}: type='{inp_type}', placeholder='{inp_placeholder}', id='{inp_id}', class='{inp_class[:50]}'")
            except Exception as e:
                logger.error(f"  Error reading input {i}: {e}")
        
        # Get all textarea elements
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        logger.info(f"📝 Thread {thread_id}: Found {len(textareas)} textarea elements")
        for i, ta in enumerate(textareas[:5]):  # Show first 5
            try:
                ta_placeholder = ta.get_attribute("placeholder") or ""
                ta_id = ta.get_attribute("id") or ""
                ta_class = ta.get_attribute("class") or ""
                logger.info(f"  Textarea {i}: placeholder='{ta_placeholder}', id='{ta_id}', class='{ta_class[:50]}'")
            except Exception as e:
                logger.error(f"  Error reading textarea {i}: {e}")
        
        # Get all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        logger.info(f"🔘 Thread {thread_id}: Found {len(buttons)} button elements")
        for i, btn in enumerate(buttons[:10]):  # Show first 10
            try:
                btn_text = btn.text[:30] if btn.text else ""
                btn_class = btn.get_attribute("class") or ""
                logger.info(f"  Button {i}: text='{btn_text}', class='{btn_class[:50]}'")
            except Exception as e:
                logger.error(f"  Error reading button {i}: {e}")
        
        # Check for login/signup elements
        login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Log in') or contains(text(), 'Sign up') or contains(text(), 'Continue') or contains(text(), 'Get started')]")
        logger.info(f"🔐 Thread {thread_id}: Found {len(login_elements)} login-related elements")
        for i, elem in enumerate(login_elements[:5]):
            try:
                elem_text = elem.text[:50] if elem.text else ""
                elem_tag = elem.tag_name
                logger.info(f"  Login element {i}: tag='{elem_tag}', text='{elem_text}'")
            except Exception as e:
                logger.error(f"  Error reading login element {i}: {e}")
        
        # Check for specific keywords in page source
        page_source = driver.page_source
        logger.info(f"📄 Thread {thread_id}: Page source length: {len(page_source)} characters")
        
        keywords = ["chat", "message", "send", "login", "continue", "textarea", "input", "prompt"]
        for keyword in keywords:
            count = page_source.lower().count(keyword)
            if count > 0:
                logger.info(f"🔍 Thread {thread_id}: Found '{keyword}' {count} times in page source")
        
        # Look for div elements with contenteditable
        contenteditable_divs = driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
        logger.info(f"📝 Thread {thread_id}: Found {len(contenteditable_divs)} contenteditable div elements")
        for i, div in enumerate(contenteditable_divs[:5]):
            try:
                div_class = div.get_attribute("class") or ""
                div_id = div.get_attribute("id") or ""
                div_data_id = div.get_attribute("data-id") or ""
                logger.info(f"  ContentEditable {i}: class='{div_class[:50]}', id='{div_id}', data-id='{div_data_id}'")
            except Exception as e:
                logger.error(f"  Error reading contenteditable {i}: {e}")
        
        # Continue to actual message sending instead of returning early
        logger.info(f"🔍 Thread {thread_id}: Scraping complete - proceeding to send message")
        
        # Find input element - Updated selectors based on scraping analysis
        input_selectors = [
            '#prompt-textarea',  # Main contenteditable div found in scraping
            'div.ProseMirror',   # ProseMirror editor class
            'textarea[placeholder*="Ask anything"]',  # Fallback textarea with correct placeholder
            'div[contenteditable="true"]',  # Generic contenteditable
            'textarea[data-id="root"]',  # Previous selector
            'textarea[placeholder*="Message"]',  # Generic message input
            'textarea'  # Final fallback
        ]
        
        found_input = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        found_input = element
                        logger.info(f"✅ Thread {thread_id}: Found input with {selector}")
                        break
                if found_input:
                    break
            except:
                continue
        
        if not found_input:
            # Debug: Get page source snippet for troubleshooting
            try:
                page_source = driver.page_source
                logger.error(f"Thread {thread_id}: Page title: {driver.title}")
                logger.error(f"Thread {thread_id}: URL: {driver.current_url}")
                # Look for any textarea or input elements
                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                inputs = driver.find_elements(By.TAG_NAME, "input")
                contenteditable = driver.find_elements(By.CSS_SELECTOR, "[contenteditable]")
                logger.error(f"Thread {thread_id}: Found {len(textareas)} textareas, {len(inputs)} inputs, {len(contenteditable)} contenteditable")
            except Exception as debug_e:
                logger.error(f"Thread {thread_id}: Debug error: {debug_e}")
            
            return f"Thread {thread_id}: No input element found"
        
        # Send message (exactly like working version)
        logger.info(f"📝 Thread {thread_id}: Sending message...")
        found_input.click()
        time.sleep(0.5)
        found_input.clear()
        found_input.send_keys(question)
        time.sleep(1)
        found_input.send_keys(Keys.RETURN)
        logger.info(f"✅ Thread {thread_id}: Message sent")
        
        # Wait for response (exactly like working debug script)
        logger.info(f"⏳ Thread {thread_id}: Waiting for response...")
        time.sleep(10)  # Same wait time as successful debug script
        
        # Look for response - Updated selectors for markdown content
        response_selectors = [
            'div[data-message-author-role="assistant"] .markdown',  # Assistant message with markdown
            'div[data-message-author-role="assistant"]',  # Assistant message container
            '[data-message-author-role="assistant"]',  # Any element with assistant role
            '.markdown',  # Direct markdown class
            '.prose',  # Prose styling class
            'div[class*="markdown"]',  # Any div with markdown in class name
            'div[class*="prose"]',  # Any div with prose in class name
            'article',  # Article elements (sometimes used for responses)
            'div[data-testid*="conversation-turn"]'  # Conversation turn elements
        ]
        
        for selector in response_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Thread {thread_id}: Selector '{selector}' found {len(elements)} elements")
                if elements:
                    response_text = elements[-1].text.strip()
                    if response_text and len(response_text) > 5:
                        logger.info(f"✅ Thread {thread_id}: Found response with {selector}: {response_text[:100]}...")
                        return response_text
            except Exception as e:
                logger.warning(f"Thread {thread_id}: Error with selector '{selector}': {e}")
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
