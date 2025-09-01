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

# Set up logging
logger = logging.getLogger(__name__)

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
                logger.info(f"🧹 Cleaned up temp directory: {temp_dir}")
            except:
                pass
        thread_local.temp_dirs = []

def get_chatgpt_response(question):
    """
    Optimized function to get ChatGPT response for parallel execution
    """
    thread_id = threading.get_ident()
    logger.info(f"🤖 Thread {thread_id}: Getting response for: {question[:50]}...")
    
    driver = None
    try:
        # Set up browser with thread-specific optimizations
        driver = setup_undetected_browser_parallel()
        driver.set_page_load_timeout(30)  # Increased timeout for parallel loads
        
        # Open ChatGPT
        logger.info(f"🌐 Thread {thread_id}: Opening ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Randomized wait to prevent simultaneous requests
        wait_time = random.uniform(4, 8)
        logger.info(f"⏱️ Thread {thread_id}: Waiting {wait_time:.1f}s for page load...")
        time.sleep(wait_time)
        
        # Find input element with better error handling
        input_element = find_input_element(driver, thread_id)
        
        if not input_element:
            return f"Thread {thread_id}: Could not find input element"
        
        # Send question
        logger.info(f"📝 Thread {thread_id}: Sending question...")
        input_element.click()
        time.sleep(0.5)
        fast_paste_typing(input_element, question)
        time.sleep(1)
        input_element.send_keys(Keys.RETURN)
        
        # Wait for response
        response = wait_for_response_complete(driver, thread_id)
        logger.info(f"✅ Thread {thread_id}: Got response ({len(response)} chars)")
        return response
        
    except Exception as e:
        error_msg = f"Thread {thread_id} Error: {str(e)}"
        logger.error(error_msg)
        return error_msg
    finally:
        if driver:
            try:
                driver.quit()
                logger.info(f"🔄 Thread {thread_id}: Browser closed")
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
            logger.info(f"� Thread {thread_id}: Looking for input element (attempt {attempt + 1}/{max_attempts})...")
            
            for selector in input_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✓ Thread {thread_id}: Found input with selector: {selector}")
                            return element
                except Exception as e:
                    logger.debug(f"Thread {thread_id}: Selector {selector} failed: {e}")
                    continue
            
            # If no element found, wait and try again
            if attempt < max_attempts - 1:
                wait_time = 3 + attempt * 2
                logger.info(f"⏳ Thread {thread_id}: No input found, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                
        except Exception as e:
            logger.error(f"❌ Thread {thread_id}: Error finding input element: {e}")
    
    logger.error(f"❌ Thread {thread_id}: Could not find input element after {max_attempts} attempts")
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
            
            # Add randomized viewport size to differentiate browser instances
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f"--window-size={width},{height}")
            
            # Randomized window position to prevent overlap
            x_pos = random.randint(0, 200)
            y_pos = random.randint(0, 200)
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
            
            logger.info(f"🚀 Thread {thread_id}: Browser created successfully with user_data_dir: {user_data_dir}")
            
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

def human_mouse_movement(driver, element):
    """
    Simulate human-like mouse movement to element
    """
    actions = ActionChains(driver)
    
    # Get element location and size
    location = element.location
    size = element.size
    
    # Calculate random point within element
    x_offset = random.randint(5, max(5, size['width'] - 5))
    y_offset = random.randint(5, max(5, size['height'] - 5))
    
    # Move to element with slight randomness
    actions.move_to_element_with_offset(element, x_offset, y_offset)
    actions.pause(random.uniform(0.5, 1.5))
    actions.click()
    actions.perform()

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
        
        print(f"✓ Fast-pasted: '{text}'")
        
    except Exception as e:
        print(f"Paste failed, using fast typing: {e}")
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
    logger.info(f"⚡ Thread {thread_id}: Fast-waiting for response...")
    
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
                        logger.info(f"✓ Thread {thread_id}: Response completed!")
                        return response_text
                else:
                    stable_count = 0
                    last_response_length = current_length
                
                # Minimal progress updates
                if i % 15 == 0 and current_length > 50:
                    logger.info(f"📝 Thread {thread_id}: Response: {current_length} chars...")
                    
                no_response_count = 0
            else:
                no_response_count += 1
                if no_response_count > 15:
                    logger.warning(f"⏰ Thread {thread_id}: No response detected...")
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
    print(f"\n⚡ Starting Ultra-Fast Iteration {iteration}")
    
    driver = None
    
    try:
        # Set up optimized browser
        print("🚀 Setting up optimized browser...")
        driver = setup_undetected_browser()
        
        # Set faster page load timeout
        driver.set_page_load_timeout(15)
        
        print("🌐 Opening ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Minimal initial wait
        initial_wait = random.uniform(4, 6)
        print(f"⏱️ Quick wait {initial_wait:.1f}s for page load...")
        time.sleep(initial_wait)
        
        # Quick page interaction to trigger load completion
        driver.execute_script("window.scrollTo(0, 50);")
        time.sleep(0.5)
        
        # Find input box with timeout optimization
        print("🔍 Fast input detection...")
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
                        print(f"✓ Found input: {selector}")
                        break
                if input_element:
                    break
            except:
                continue
        
        if not input_element:
            print("🔄 Alternative input detection...")
            all_inputs = driver.find_elements(By.TAG_NAME, "textarea")
            for inp in all_inputs:
                if inp.is_displayed() and inp.is_enabled():
                    input_element = inp
                    break
        
        if not input_element:
            print("❌ No input found!")
            return
        
        # Ultra-fast interaction
        print("⚡ Ultra-fast input interaction...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
        time.sleep(0.3)
        
        # Quick click and focus
        input_element.click()
        time.sleep(0.2)
        
        # Fast text input using clipboard paste
        question = "what is best laptop to buy in 2024"
        print(f"📝 Fast-typing: '{question}'")
        fast_paste_typing(input_element, question)
        
        # Minimal thinking pause
        thinking_pause = random.uniform(0.5, 1.5)
        print(f"🤔 Quick think: {thinking_pause:.1f}s...")
        time.sleep(thinking_pause)
        
        # Send message
        print("📤 Sending message...")
        input_element.send_keys(Keys.RETURN)
        
        # Fast response waiting
        response_text = wait_for_response_complete(driver)
        
        # Display results
        print(f"\n📋 RESPONSE {iteration}")
        if response_text and len(response_text) > 30 and "blocked" not in response_text.lower():
            print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
            try:
                pyperclip.copy(response_text)
                print("\n✅ Copied to clipboard!")
            except:
                print("\n⚠️ Could not copy")
        else:
            print("❌ No valid response")
            print(f"Got: {response_text[:100]}...")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error {iteration}: {e}")
    
    finally:
        if driver:
            try:
                print(f"🔄 Closing browser {iteration}...")
                driver.quit()
                print(f"✅ Browser {iteration} closed!")
            except:
                print(f"⚠️ Browser {iteration} cleanup issues")
                pass

def run_automation():
    """
    Run ULTRA-SPEED automation with optimized browser switching
    """
    print("🚀 ULTRA-SPEED ChatGPT Automation - 5 iterations")
    print("⚡ Maximum speed optimization enabled!")
    
    for i in range(1, 6):
        try:
            start_time = time.time()
            automated_chatgpt_query(i)
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"⏱️ Iteration {i} completed in {duration:.1f} seconds")
            
            # Minimal delay between iterations for system stability
            if i < 5:
                print(f"\n⚡ Starting iteration {i+1} in 1 second...")
                time.sleep(1)  # Just 1 second between iterations
                
        except KeyboardInterrupt:
            print(f"\n⛔ Stopped at iteration {i}")
            break
        except Exception as e:
            print(f"❌ Error in iteration {i}: {e}")
            # Quick recovery - just 2 seconds wait on error
            time.sleep(2)
            continue
    
    print("\n🎉 ULTRA-SPEED AUTOMATION COMPLETED!")
    print("🚀 All iterations finished at maximum speed!")

if __name__ == "__main__":
    run_automation()
