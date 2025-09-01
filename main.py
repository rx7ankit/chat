import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyperclip
import random

def setup_undetected_browser():
    """
    Set up optimized undetected Chrome browser
    """
    options = uc.ChromeOptions()
    
    # Performance optimizations
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
    
    # Network optimizations
    options.add_argument("--aggressive-cache-discard")
    options.add_argument("--memory-pressure-off")
    
    # Create undetected Chrome instance
    driver = uc.Chrome(options=options, version_main=None)
    
    # Set faster page load strategy
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    
    # Additional stealth measures
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    return driver

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

def wait_for_response_complete(driver, max_wait=60):
    """
    Optimized response waiting with faster detection
    """
    print("⚡ Fast-waiting for response...")
    
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
                        print("✓ Response completed!")
                        return response_text
                else:
                    stable_count = 0
                    last_response_length = current_length
                
                # Minimal progress updates
                if i % 15 == 0 and current_length > 50:
                    print(f"📝 Response: {current_length} chars...")
                    
                no_response_count = 0
            else:
                no_response_count += 1
                if no_response_count > 15:
                    print("⏰ No response detected...")
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
    
    return "No response received"

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
