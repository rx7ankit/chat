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
    Set up undetected Chrome browser
    """
    options = uc.ChromeOptions()
    
    # Basic settings
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-default-browser-check")
    
    # Create undetected Chrome instance
    driver = uc.Chrome(options=options, version_main=None)
    
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

def human_like_typing(element, text):
    """
    Type text with optimized human-like patterns (faster)
    """
    # Type words with slight delays instead of character by character
    words = text.split(' ')
    
    for i, word in enumerate(words):
        # Type word faster but still natural
        for char in word:
            element.send_keys(char)
            # Faster typing with smaller delays
            if char in 'aeiou':  # Vowels typed faster
                time.sleep(random.uniform(0.03, 0.08))
            else:
                time.sleep(random.uniform(0.05, 0.12))
        
        # Add space after word (except last word)
        if i < len(words) - 1:
            element.send_keys(' ')
            time.sleep(random.uniform(0.1, 0.3))  # Shorter pause between words
        
        # Reduced thinking pauses
        if random.random() < 0.15:  # 15% chance instead of 25%
            time.sleep(random.uniform(0.3, 1.0))

def wait_for_response_complete(driver, max_wait=80):
    """
    Wait until ChatGPT finishes generating the response (optimized)
    """
    print("Waiting for response...")
    
    # Shorter initial wait
    time.sleep(5)
    
    last_response_length = 0
    stable_count = 0
    no_response_count = 0
    
    for i in range(max_wait):
        try:
            # Streamlined response detection
            response_selectors = [
                'div[data-message-author-role="assistant"]',
                'div[data-message-role="assistant"]',
                '.prose'
            ]
            
            response_text = ""
            for selector in response_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        response_text = elements[-1].text.strip()
                        if response_text and "Something went wrong" not in response_text and len(response_text) > 20:
                            break
                except:
                    continue
            
            if response_text and "Something went wrong" not in response_text and len(response_text) > 20:
                current_length = len(response_text)
                
                # Faster stability check - only 3 seconds
                if current_length == last_response_length and current_length > 80:
                    stable_count += 1
                    if stable_count >= 3:  # Stable for only 3 seconds
                        print("Response completed!")
                        return response_text
                else:
                    stable_count = 0
                    last_response_length = current_length
                
                # Less frequent progress updates
                if i % 10 == 0 and current_length > 100:
                    print(f"Response: {current_length} chars...")
                    
                no_response_count = 0
            else:
                no_response_count += 1
                if no_response_count > 20:
                    print("No response detected...")
                    break
        
        except Exception as e:
            pass
        
        time.sleep(1)
    
    # Quick final attempt
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-message-author-role="assistant"]')
        if elements:
            final_response = elements[-1].text.strip()
            if final_response and "Something went wrong" not in final_response:
                return final_response
    except:
        pass
    
    return "No response received"

def automated_chatgpt_query(iteration):
    """
    Optimized anti-detection ChatGPT automation
    """
    print(f"\n=== Starting Iteration {iteration} ===")
    
    driver = None
    
    try:
        # Set up undetected browser
        print("Setting up browser...")
        driver = setup_undetected_browser()
        
        print("Opening ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Reduced initial wait but still safe
        initial_wait = random.uniform(8, 12)
        print(f"Waiting {initial_wait:.1f} seconds for page load...")
        time.sleep(initial_wait)
        
        # Quick page interaction
        driver.execute_script("window.scrollTo(0, 100);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find input box faster
        print("Finding input box...")
        wait = WebDriverWait(driver, 30)
        
        input_selectors = [
            'textarea[data-testid="prompt-textarea"]',
            'div[contenteditable="true"]',
            'textarea'
        ]
        
        input_element = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            input_element = element
                            print(f"Found input: {selector}")
                            break
                if input_element:
                    break
            except:
                continue
        
        if not input_element:
            print("Trying alternative input detection...")
            all_inputs = driver.find_elements(By.TAG_NAME, "textarea")
            for inp in all_inputs:
                if inp.is_displayed() and inp.is_enabled():
                    input_element = inp
                    break
        
        if not input_element:
            print("No input found!")
            return
        
        # Faster interaction
        print("Interacting with input...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
        time.sleep(1)
        
        # Quick click
        input_element.click()
        time.sleep(0.5)
        
        # Clear and type faster
        input_element.clear()
        time.sleep(0.2)
        
        # Faster typing
        question = "what is best laptop to buy"
        print(f"Typing: '{question}'")
        human_like_typing(input_element, question)
        
        # Shorter thinking pause
        thinking_pause = random.uniform(1, 3)
        print(f"Thinking: {thinking_pause:.1f}s...")
        time.sleep(thinking_pause)
        
        # Send message
        print("Sending...")
        input_element.send_keys(Keys.RETURN)
        
        # Wait for response
        response_text = wait_for_response_complete(driver)
        
        # Display results
        print(f"\n=== RESPONSE {iteration} ===")
        if response_text and len(response_text) > 50 and "blocked" not in response_text.lower():
            print(response_text)
            try:
                pyperclip.copy(response_text)
                print("\n✓ Copied to clipboard!")
            except:
                print("\n! Could not copy")
        else:
            print("No valid response")
            print(f"Got: {response_text[:100]}...")
        print("=" * 50)
        
        # Minimal closing pause - just enough for response copy
        time.sleep(1)
        
    except Exception as e:
        print(f"Error {iteration}: {e}")
    
    finally:
        if driver:
            try:
                print(f"🔄 Closing browser {iteration}...")
                driver.quit()
                # Immediate cleanup - no delay
                print(f"✓ Browser {iteration} closed - ready for next!")
            except:
                print(f"! Browser {iteration} cleanup had minor issues")
                pass

def run_automation():
    """
    Run ultra-fast automation with immediate browser switching
    """
    print("🚀 Starting ULTRA-FAST ChatGPT Automation - 5 iterations")
    print("🔄 Immediate browser switching for maximum speed!")
    
    for i in range(1, 6):
        try:
            automated_chatgpt_query(i)
            
            # NO DELAY between iterations - immediate next browser!
            if i < 5:
                print(f"\n⚡ Starting iteration {i+1} immediately...")
                # Just a tiny 2-second buffer for system cleanup
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n⛔ Stopped at iteration {i}")
            break
        except Exception as e:
            print(f"❌ Error in iteration {i}: {e}")
            # Even on error, just wait 3 seconds and continue
            time.sleep(3)
            continue
    
    print("\n🎉 AUTOMATION COMPLETED!")

if __name__ == "__main__":
    run_automation()
