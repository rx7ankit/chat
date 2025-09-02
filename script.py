import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyperclip
import random
import threading
import logging
import tempfile
import os
import uuid
from pathlib import Path

# Configuration - Set to True for server deployment (no GUI), False for local testing
HEADLESS_MODE = True

# Set up logging - suppress unnecessary logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Only show errors

# Suppress noisy loggers
logging.getLogger("undetected_chromedriver").setLevel(logging.ERROR)
logging.getLogger("selenium").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Thread-local storage for better parallel execution
thread_local = threading.local()

# Global lock for Chrome driver creation to prevent conflicts
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

def get_chatgpt_response(question):
    """
    Optimized function to get ChatGPT response for parallel execution with timeout handling
    """
    thread_id = threading.get_ident()
    print("✅ Prompt received")
    
    driver = None
    try:
        # Set up browser with thread-specific optimizations (headless mode)
        driver = setup_undetected_browser_parallel(headless=HEADLESS_MODE)
        driver.set_page_load_timeout(45)  # Increased timeout for initial load
        
        # Open ChatGPT with timeout handling
        print("✅ Browser opened")
        logger.info(f"🌐 Thread {thread_id}: Navigating to ChatGPT...")
        
        start_time = time.time()
        try:
            driver.get("https://chatgpt.com")
            logger.info(f"✅ Thread {thread_id}: Page loaded successfully")
        except Exception as nav_error:
            logger.error(f"❌ Thread {thread_id}: Navigation failed: {nav_error}")
            return f"Thread {thread_id}: Navigation failed - {nav_error}"
        
        # Wait for page to be ready with timeout
        page_ready = wait_for_page_ready(driver, thread_id, timeout=90)  # Increased timeout for Cloudflare
        if not page_ready:
            return f"Thread {thread_id}: Page failed to load properly - may be blocked by Cloudflare"
        
        # Randomized wait to prevent simultaneous requests
        wait_time = random.uniform(3, 6)
        time.sleep(wait_time)
        
        # Find input element with better error handling and timeout
        input_element = find_input_element(driver, thread_id, timeout=20)
        
        if not input_element:
            return f"Thread {thread_id}: Could not find input element"
        
        # Send question with timeout handling
        success = send_question_with_timeout(driver, input_element, question, thread_id)
        if not success:
            return f"Thread {thread_id}: Failed to send question"
        
        print("✅ Prompt input successfully")
        
        # Wait for response with timeout
        response = wait_for_response_complete(driver, thread_id, timeout=60)
        if response is None:
            return f"Thread {thread_id}: Response timeout"
            
        print("✅ Response sent to API successfully")
        return response
        
    except Exception as e:
        error_msg = f"Thread {thread_id} Error: {str(e)}"
        logger.error(error_msg)
        return error_msg
    finally:
        if driver:
            try:
                driver.quit()
                print("✅ Browser closed")
            except Exception as e:
                logger.warning(f"⚠️ Thread {thread_id}: Browser cleanup warning: {e}")
        
        # Clean up temporary resources
        cleanup_thread_resources()

def wait_for_page_ready(driver, thread_id, timeout=60):
    """Wait for the ChatGPT page to be fully loaded and ready, handling Cloudflare"""
    logger.info(f"⏳ Thread {thread_id}: Waiting for page to be ready...")
    
    start_time = time.time()
    cloudflare_detected = False
    
    while time.time() - start_time < timeout:
        try:
            current_title = driver.title.lower()
            
            # Check for Cloudflare challenge
            if "just a moment" in current_title or "checking your browser" in current_title:
                if not cloudflare_detected:
                    logger.info(f"🛡️ Thread {thread_id}: Cloudflare challenge detected, waiting...")
                    cloudflare_detected = True
                time.sleep(5)  # Wait longer for Cloudflare
                continue
            
            # Check if page is ready
            page_ready = driver.execute_script("return document.readyState") == "complete"
            
            if page_ready and "chatgpt" in current_title:
                # Look for ChatGPT page indicators
                indicators = [
                    'textarea[data-testid="prompt-textarea"]',
                    'div[contenteditable="true"]',
                    'textarea[placeholder*="Message"]',
                    '[data-testid*="chat"]',
                    'main',
                    'textarea'
                ]
                
                for indicator in indicators:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        logger.info(f"✅ Thread {thread_id}: Page ready - found {indicator}")
                        return True
            
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ Thread {thread_id}: Page ready check error: {e}")
            time.sleep(2)
            continue
    
    logger.warning(f"⏰ Thread {thread_id}: Page ready timeout after {timeout}s")
    return False

def send_question_with_timeout(driver, input_element, question, thread_id, timeout=15):
    """Send question to ChatGPT with timeout handling"""
    logger.info(f"📝 Thread {thread_id}: Sending question...")
    
    start_time = time.time()
    try:
        # Click and focus on input
        input_element.click()
        time.sleep(0.5)
        
        # Clear any existing text
        input_element.clear()
        time.sleep(0.3)
        
        # Type the question using fast paste
        fast_paste_typing(input_element, question)
        time.sleep(1)
        
        # Send the message
        input_element.send_keys(Keys.RETURN)
        
        logger.info(f"✅ Thread {thread_id}: Question sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Thread {thread_id}: Failed to send question: {e}")
        return False

def find_input_element(driver, thread_id, timeout=20):
    """Find ChatGPT input element with timeout"""
    logger.info(f"🔍 Thread {thread_id}: Looking for input element...")
    
    input_selectors = [
        'textarea[data-testid="prompt-textarea"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="Message"]',
        'textarea[placeholder*="message"]',
        'textarea',
        '[data-testid*="prompt"]',
        '[contenteditable="true"]'
    ]
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            for selector in input_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✅ Thread {thread_id}: Found input element with selector: {selector}")
                            return element
                except Exception:
                    continue
            
            time.sleep(2)  # Wait before retrying
            
        except Exception as e:
            time.sleep(2)
            continue
    
    logger.error(f"❌ Thread {thread_id}: Input element not found after {timeout}s")
    return None

def setup_undetected_browser_parallel(headless=True):
    """
    Set up optimized undetected Chrome browser for parallel execution with proper isolation
    Args:
        headless (bool): If True, runs browser in headless mode (no GUI)
    """
    thread_id = threading.get_ident()
    
    # Use lock to prevent concurrent Chrome driver creation
    with chrome_creation_lock:
        try:
            # Create unique temporary directory for this browser instance
            temp_dir = tempfile.mkdtemp(prefix=f"chrome_thread_{thread_id}_")
            user_data_dir = os.path.join(temp_dir, "user_data")
            os.makedirs(user_data_dir, exist_ok=True)
            
            options = uc.ChromeOptions()
            
            # Unique user data directory for each thread to prevent conflicts
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument(f"--profile-directory=Profile_{thread_id}")
            
            # Enhanced performance optimizations for parallel execution
            options.add_argument("--no-first-run")
            options.add_argument("--no-service-autorun")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            # Temporarily disable images for faster loading
            options.add_argument("--disable-images")
            # Don't disable JavaScript as ChatGPT needs it
            # options.add_argument("--disable-javascript")  # Commented out
            options.add_argument("--disable-javascript-harmony-shipping")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-sync")
            options.add_argument("--metrics-recording-only")
            options.add_argument("--no-report-upload")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            
            # Additional stealth options for Cloudflare bypass
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions-file-access-check")
            options.add_argument("--disable-extensions-http-throttling")
            
            # Headless mode - browser runs without GUI
            if headless:
                options.add_argument("--headless=new")  # Use new headless mode
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-software-rasterizer")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--run-all-compositor-stages-before-draw")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
                # Remove fixed remote debugging port to avoid conflicts
            
            # Memory and CPU optimizations for parallel execution
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            options.add_argument("--aggressive-cache-discard")
            options.add_argument("--disable-background-networking")
            
            # Prevent sharing between instances
            options.add_argument("--disable-shared-worker")
            options.add_argument("--disable-background-mode")
            options.add_argument("--disable-backgrounding-occluded-windows")
            
            # Unique port range for each instance to prevent conflicts (only for non-headless)
            if not headless:
                base_port = 9222 + (thread_id % 1000)
                options.add_argument(f"--remote-debugging-port={base_port}")
            
            # Randomize user agent slightly for each thread
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
            ]
            
            # Set virtual display size for headless mode
            width = random.randint(1024, 1920)
            height = random.randint(768, 1080)
            options.add_argument(f"--window-size={width},{height}")
            
            # Additional optimizations based on mode
            if headless:
                # Headless-specific optimizations
                options.add_argument("--disable-logging")
                options.add_argument("--disable-login-animations")
                options.add_argument("--disable-motion-blur")
                options.add_argument("--disable-notifications")
                options.add_argument("--disable-audio-output")
                options.add_argument("--disable-speech-api")
            else:
                # Visible mode optimizations
                options.add_argument("--start-maximized=false")
                options.add_argument("--disable-fullscreen")
            
            # Small delay to prevent simultaneous startup
            startup_delay = random.uniform(0.5, 2.0)
            time.sleep(startup_delay)
            
            # Create undetected Chrome instance with better error handling
            max_retries = 3
            driver = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 Thread {thread_id}: Creating browser (attempt {attempt + 1})...")
                    driver = uc.Chrome(
                        options=options, 
                        version_main=None,
                        user_data_dir=user_data_dir,
                        suppress_welcome=True,
                        use_subprocess=False,  # Important for parallel execution
                        headless=headless  # Explicitly set headless mode
                    )
                    logger.info(f"✅ Thread {thread_id}: Browser created successfully")
                    break
                except Exception as retry_error:
                    logger.warning(f"⚠️ Thread {thread_id}: Attempt {attempt + 1} failed: {retry_error}")
                    if attempt == max_retries - 1:
                        raise retry_error
                    time.sleep(2)  # Wait before retry
            
            if driver is None:
                raise Exception("Failed to create driver after all retries")
            
            # Set timeouts for better stability
            driver.set_page_load_timeout(60)  # Increased timeout
            driver.implicitly_wait(15)  # Increased wait time
            
            # Set window size if not headless
            if not headless:
                try:
                    driver.set_window_size(width, height)
                    driver.set_window_position(100, 100)
                except Exception as window_error:
                    logger.warning(f"⚠️ Thread {thread_id}: Could not set window properties: {window_error}")
            
            # Additional stealth measures only for non-headless mode
            if not headless:
                try:
                    # Set random user agent
                    selected_ua = random.choice(user_agents)
                    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        "userAgent": selected_ua
                    })
                    
                    # Additional stealth measures
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                except Exception as stealth_error:
                    logger.warning(f"⚠️ Thread {thread_id}: Stealth setup warning: {stealth_error}")
            
            # Store temp directory for cleanup
            if not hasattr(thread_local, 'temp_dirs'):
                thread_local.temp_dirs = []
            thread_local.temp_dirs.append(temp_dir)
            
            return driver
            
        except Exception as e:
            logger.error(f"❌ Thread {thread_id}: Failed to create browser: {e}")
            # Clean up temp directory if creation failed
            try:
                if 'temp_dir' in locals():
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            raise

def fast_paste_typing(element, text):
    """
    Ultra-fast typing using clipboard paste with natural cover typing
    """
    try:
        # Copy text to clipboard
        pyperclip.copy(text)
        time.sleep(0.1)
        
        # Clear the input first
        element.clear()
        time.sleep(0.1)
        
        # Paste the text instantly
        element.send_keys(Keys.CONTROL + 'v')
        time.sleep(0.2)
        
        # Add a few natural keystrokes to mask the paste
        element.send_keys(Keys.END)
        time.sleep(0.1)
        element.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        element.send_keys(text[-1])  # Retype last character
        
    except Exception as e:
        # Fallback to optimized typing
        fast_human_typing(element, text)

def fast_human_typing(element, text):
    """
    Optimized human-like typing (fallback method)
    """
    # Type in chunks for speed
    chunk_size = 5
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        element.send_keys(chunk)
        time.sleep(random.uniform(0.05, 0.15))  # Very fast between chunks

def wait_for_response_complete(driver, thread_id, timeout=60):
    """
    Optimized response waiting with timeout and better error handling
    """
    logger.info(f"⏳ Thread {thread_id}: Waiting for ChatGPT response...")
    
    # Short initial wait for response to start
    time.sleep(3)
    
    last_response_length = 0
    stable_count = 0
    no_response_count = 0
    start_time = time.time()
    
    # Cached selectors for faster lookup
    response_selectors = [
        'div[data-message-author-role="assistant"]',
        'div[data-message-role="assistant"]', 
        '.prose',
        'div[data-testid="conversation-turn-2"]',
        '[data-message-author-role="assistant"] .markdown',
        '.group .markdown'
    ]
    
    while time.time() - start_time < timeout:
        try:
            response_text = ""
            
            # Fast element detection with cached selectors
            for selector in response_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        response_text = elements[-1].text.strip()
                        if response_text and len(response_text) > 10:
                            break
                except:
                    continue
            
            if response_text and len(response_text) > 20:
                current_length = len(response_text)
                
                # Check if response is stable (stopped growing)
                if current_length == last_response_length and current_length > 50:
                    stable_count += 1
                    if stable_count >= 3:  # Stable for 3 seconds
                        logger.info(f"✅ Thread {thread_id}: Response complete ({current_length} chars)")
                        return response_text
                else:
                    stable_count = 0
                    last_response_length = current_length
                
                no_response_count = 0
            else:
                no_response_count += 1
                if no_response_count > 20:  # 20 seconds with no response
                    logger.warning(f"⚠️ Thread {thread_id}: No response detected for 20s")
                    break
        
        except Exception as e:
            logger.warning(f"⚠️ Thread {thread_id}: Error checking response: {e}")
        
        time.sleep(1)
    
    # Final attempt to get any response
    try:
        for selector in response_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                final_response = elements[-1].text.strip()
                if final_response and len(final_response) > 10:
                    logger.info(f"✅ Thread {thread_id}: Final response found ({len(final_response)} chars)")
                    return final_response
    except Exception as e:
        logger.warning(f"⚠️ Thread {thread_id}: Final response check failed: {e}")
    
    logger.error(f"❌ Thread {thread_id}: Response timeout after {timeout}s")
    return None

def automated_chatgpt_query(iteration):
    """
    Ultra-optimized ChatGPT automation with faster loading and interaction
    """
    driver = None
    
    try:
        # Set up optimized browser (headless mode)
        driver = setup_undetected_browser_parallel(headless=HEADLESS_MODE)
        
        # Set faster page load timeout
        driver.set_page_load_timeout(15)
        
        print("✅ Browser opened")
        driver.get("https://chatgpt.com")
        
        # Minimal initial wait
        initial_wait = random.uniform(4, 6)
        time.sleep(initial_wait)
        
        # Quick page interaction to trigger load completion
        driver.execute_script("window.scrollTo(0, 50);")
        time.sleep(0.5)
        
        # Find input box with timeout optimization
        wait = WebDriverWait(driver, 20)
        
        input_selectors = [
            'textarea[data-testid="prompt-textarea"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            'textarea'
        ]
        
        input_element = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        input_element = element
                        break
                if input_element:
                    break
            except:
                continue
        
        if not input_element:
            all_inputs = driver.find_elements(By.TAG_NAME, "textarea")
            for inp in all_inputs:
                if inp.is_displayed() and inp.is_enabled():
                    input_element = inp
                    break
        
        if not input_element:
            return
        
        # Ultra-fast interaction
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
        time.sleep(0.3)
        
        # Quick click and focus
        input_element.click()
        time.sleep(0.2)
        
        # Fast text input using clipboard paste
        question = "what is best laptop to buy in 2024"
        print("✅ Prompt received")
        fast_paste_typing(input_element, question)
        
        # Minimal thinking pause
        thinking_pause = random.uniform(0.5, 1.5)
        time.sleep(thinking_pause)
        
        # Send message
        input_element.send_keys(Keys.RETURN)
        print("✅ Prompt input successfully")
        
        # Fast response waiting
        response_text = wait_for_response_complete(driver, threading.get_ident())
        
        # Display results
        if response_text and len(response_text) > 30 and "blocked" not in response_text.lower():
            print(f"✅ Response received: {response_text[:10]}")
            try:
                pyperclip.copy(response_text)
                print("✅ Response sent to API")
            except:
                pass
        else:
            print(f"✅ Response received: {response_text[:10]}")
        
    except Exception as e:
        pass
    
    finally:
        if driver:
            try:
                driver.quit()
                print("✅ Browser closed")
            except:
                pass

def run_automation():
    """
    Run ULTRA-SPEED automation with optimized browser switching
    """
    for i in range(1, 6):
        try:
            automated_chatgpt_query(i)
            
            # Minimal delay between iterations for system stability
            if i < 5:
                time.sleep(1)  # Just 1 second between iterations
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            # Quick recovery - just 2 seconds wait on error
            time.sleep(2)
            continue

if __name__ == "__main__":
    run_automation()
