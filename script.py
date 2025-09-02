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
    Optimized function to get ChatGPT response for parallel execution
    """
    thread_id = threading.get_ident()
    print("✅ Prompt received")
    
    driver = None
    try:
        # Set up browser with thread-specific optimizations
        driver = setup_undetected_browser_parallel()
        driver.set_page_load_timeout(30)  # Increased timeout for parallel loads
        
        # Open ChatGPT
        print("✅ Browser opened")
        driver.get("https://chatgpt.com")
        
        # Randomized wait to prevent simultaneous requests
        wait_time = random.uniform(4, 8)
        time.sleep(wait_time)
        
        # Find input element with better error handling
        input_element = find_input_element(driver, thread_id)
        
        if not input_element:
            return f"Thread {thread_id}: Could not find input element"
        
        # Send question
        input_element.click()
        time.sleep(0.5)
        fast_paste_typing(input_element, question)
        time.sleep(1)
        input_element.send_keys(Keys.RETURN)
        print("✅ Prompt input successfully")
        
        # Wait for response
        response = wait_for_response_complete(driver, thread_id)
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

def find_input_element(driver, thread_id):
    """Find ChatGPT input element with better error handling"""
    input_selectors = [
        'textarea[data-testid="prompt-textarea"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="Message"]',
        'textarea[placeholder*="message"]',
        'textarea'
    ]
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            for selector in input_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            return element
                except Exception as e:
                    continue
            
            # If no element found, wait and try again
            if attempt < max_attempts - 1:
                wait_time = 3 + attempt * 2
                time.sleep(wait_time)
                
        except Exception as e:
            pass
    
    return None

def setup_undetected_browser_parallel():
    """
    Set up optimized undetected Chrome browser for parallel execution with proper isolation
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
            options.add_argument("--disable-images")  # Skip loading images for faster page load
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
            
            # Memory and CPU optimizations for parallel execution
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            options.add_argument("--aggressive-cache-discard")
            options.add_argument("--disable-background-networking")
            
            # Prevent sharing between instances
            options.add_argument("--disable-shared-worker")
            options.add_argument("--disable-background-mode")
            options.add_argument("--disable-backgrounding-occluded-windows")
            
            # Unique port range for each instance to prevent conflicts
            base_port = 9222 + (thread_id % 1000)
            options.add_argument(f"--remote-debugging-port={base_port}")
            
            # Randomize user agent slightly for each thread
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
            ]
            
            # Add smaller randomized viewport size to differentiate browser instances
            width = random.randint(800, 1200)  # Smaller width range
            height = random.randint(600, 800)   # Smaller height range
            options.add_argument(f"--window-size={width},{height}")
            
            # Additional options to ensure smaller window
            options.add_argument("--start-maximized=false")
            options.add_argument("--disable-fullscreen")
            
            # Randomized window position to prevent overlap
            x_pos = random.randint(0, 400)  # Increased position range since windows are smaller
            y_pos = random.randint(0, 300)
            options.add_argument(f"--window-position={x_pos},{y_pos}")
            
            # Small delay to prevent simultaneous startup
            startup_delay = random.uniform(0.5, 2.0)
            time.sleep(startup_delay)
            
            # Create undetected Chrome instance with unique version path
            driver = uc.Chrome(
                options=options, 
                version_main=None,
                user_data_dir=user_data_dir,
                suppress_welcome=True,
                use_subprocess=False  # Important for parallel execution
            )
            
            # Force set window size after creation (this ensures it works)
            driver.set_window_size(width, height)
            driver.set_window_position(x_pos, y_pos)
            
            # Set random user agent
            selected_ua = random.choice(user_agents)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": selected_ua
            })
            
            # Additional stealth measures
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
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
        
        # Paste the text instantly
        element.send_keys(Keys.CONTROL + 'v')
        time.sleep(0.2)
        
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

def wait_for_response_complete(driver, thread_id, max_wait=60):
    """
    Optimized response waiting with faster detection for parallel execution
    """
    # Very short initial wait
    time.sleep(2)
    
    last_response_length = 0
    stable_count = 0
    no_response_count = 0
    
    # Cached selectors for faster lookup
    response_selectors = [
        'div[data-message-author-role="assistant"]',
        'div[data-message-role="assistant"]', 
        '.prose',
        'div[data-testid="conversation-turn-2"]'
    ]
    
    for i in range(max_wait):
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
                
                # Ultra-fast stability check - just 2 seconds
                if current_length == last_response_length and current_length > 50:
                    stable_count += 1
                    if stable_count >= 2:  # Stable for only 2 seconds
                        return response_text
                else:
                    stable_count = 0
                    last_response_length = current_length
                
                # Minimal progress updates
                if i % 15 == 0 and current_length > 50:
                    pass
                    
                no_response_count = 0
            else:
                no_response_count += 1
                if no_response_count > 15:
                    break
        
        except Exception as e:
            pass
        
        time.sleep(1)
    
    # Quick final attempt
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-message-author-role="assistant"]')
        if elements:
            final_response = elements[-1].text.strip()
            if final_response and len(final_response) > 10:
                return final_response
    except:
        pass
    
    return f"Thread {thread_id}: No response received"

def automated_chatgpt_query(iteration):
    """
    Ultra-optimized ChatGPT automation with faster loading and interaction
    """
    driver = None
    
    try:
        # Set up optimized browser
        driver = setup_undetected_browser_parallel()
        
        # Set faster page load timeout
        driver.set_page_load_timeout(15)
        
        print("✅ Browser opened")
        driver.get("https://chatgpt.com")
        
        time.sleep(0)
        
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

