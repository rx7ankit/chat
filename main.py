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
    Type text with very human-like patterns
    """
    words = text.split(' ')
    
    for i, word in enumerate(words):
        # Type each character with realistic delays
        for char in word:
            element.send_keys(char)
            # Vary typing speed realistically
            if char in 'aeiou':  # Vowels typed slightly faster
                time.sleep(random.uniform(0.08, 0.15))
            elif char in 'qwerty':  # Common letters faster
                time.sleep(random.uniform(0.1, 0.18))
            else:
                time.sleep(random.uniform(0.12, 0.25))
        
        # Add space after word (except last word)
        if i < len(words) - 1:
            element.send_keys(' ')
            time.sleep(random.uniform(0.3, 0.6))  # Pause between words
        
        # Random thinking pause after some words
        if random.random() < 0.25:  # 25% chance
            time.sleep(random.uniform(0.8, 2.5))

def wait_for_response_complete(driver, max_wait=120):
    """
    Wait until ChatGPT finishes generating the response
    """
    print("Waiting for response to be generated...")
    
    # Initial wait for response to start
    time.sleep(8)
    
    last_response_length = 0
    stable_count = 0
    no_response_count = 0
    
    for i in range(max_wait):
        try:
            # Multiple strategies to find response
            response_selectors = [
                'div[data-message-author-role="assistant"]',
                'div[data-message-role="assistant"]',
                '.markdown.prose',
                'div.prose',
                'div[data-testid*="conversation-turn"] div.prose'
            ]
            
            response_text = ""
            for selector in response_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Get the last (most recent) response
                        response_text = elements[-1].text.strip()
                        if response_text and "Something went wrong" not in response_text and len(response_text) > 20:
                            break
                except:
                    continue
            
            if response_text and "Something went wrong" not in response_text and len(response_text) > 20:
                current_length = len(response_text)
                
                # Check if response is stable (not growing)
                if current_length == last_response_length and current_length > 100:
                    stable_count += 1
                    if stable_count >= 6:  # Stable for 6 seconds
                        print("Response generation completed!")
                        return response_text
                else:
                    stable_count = 0
                    last_response_length = current_length
                
                # Progress update every 15 seconds
                if i % 15 == 0:
                    print(f"Response length: {current_length} characters... (waiting for completion)")
                    
                no_response_count = 0
            else:
                no_response_count += 1
                if no_response_count > 30:  # No valid response for 30 seconds
                    print("No valid response detected for 30 seconds...")
                    
                    # Check for error messages
                    error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Something went wrong')]")
                    if error_elements:
                        print("Error message detected, ChatGPT blocked the request")
                        return "ChatGPT blocked the automation request"
        
        except Exception as e:
            pass
        
        time.sleep(1)
    
    # Final attempt to get any response
    try:
        for selector in ['div[data-message-author-role="assistant"]', '.prose', '.markdown']:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                final_response = elements[-1].text.strip()
                if final_response and "Something went wrong" not in final_response:
                    return final_response
    except:
        pass
    
    return "No valid response received within timeout"

def automated_chatgpt_query(iteration):
    """
    Advanced anti-detection ChatGPT automation
    """
    print(f"\n=== Starting Iteration {iteration} ===")
    
    driver = None
    
    try:
        # Set up undetected browser
        print("Setting up undetected browser...")
        driver = setup_undetected_browser()
        
        print("Opening ChatGPT...")
        driver.get("https://chatgpt.com")
        
        # Extended wait for page to fully load
        initial_wait = random.uniform(12, 18)
        print(f"Waiting {initial_wait:.1f} seconds for complete page load...")
        time.sleep(initial_wait)
        
        # Human-like page interaction - scroll a bit
        driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 300));")
        time.sleep(random.uniform(2, 4))
        driver.execute_script("window.scrollTo(0, 0);")  # Scroll back to top
        time.sleep(random.uniform(1, 2))
        
        # Look for input box with extended patience
        print("Looking for input box...")
        wait = WebDriverWait(driver, 60)
        
        input_selectors = [
            'textarea[data-testid="prompt-textarea"]',
            'textarea[placeholder*="Message"]',
            'div[contenteditable="true"]',
            '#prompt-textarea',
            'textarea'
        ]
        
        input_element = None
        for selector in input_selectors:
            try:
                print(f"Trying selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            input_element = element
                            print(f"Found input box with selector: {selector}")
                            break
                if input_element:
                    break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue
        
        if not input_element:
            print("Input box not found, trying alternative methods...")
            # Try to find any visible input element
            all_inputs = driver.find_elements(By.TAG_NAME, "textarea") + driver.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
            for inp in all_inputs:
                if inp.is_displayed() and inp.is_enabled():
                    input_element = inp
                    print("Found alternative input element")
                    break
        
        if not input_element:
            print("No input element found!")
            return
        
        # Human-like interaction sequence
        print("Preparing to interact with input...")
        
        # Scroll to input with smooth behavior
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_element)
        time.sleep(random.uniform(3, 5))
        
        # Move mouse naturally to input
        print("Moving to input box...")
        human_mouse_movement(driver, input_element)
        time.sleep(random.uniform(1, 3))
        
        # Focus the input
        input_element.click()
        time.sleep(random.uniform(0.5, 1.5))
        
        # Clear any existing text
        input_element.clear()
        time.sleep(random.uniform(0.3, 0.8))
        
        # Type the question naturally
        question = "what is best laptop to buy"
        print(f"Typing question naturally: '{question}'")
        human_like_typing(input_element, question)
        
        # Human thinking pause before sending
        thinking_pause = random.uniform(3, 7)
        print(f"Thinking pause: {thinking_pause:.1f} seconds...")
        time.sleep(thinking_pause)
        
        # Send the message
        print("Sending message...")
        input_element.send_keys(Keys.RETURN)
        
        # Wait for complete response
        response_text = wait_for_response_complete(driver)
        
        # Display results
        print(f"\n=== RESPONSE FOR ITERATION {iteration} ===")
        if response_text and len(response_text) > 50 and "blocked" not in response_text.lower():
            print(response_text)
            try:
                pyperclip.copy(response_text)
                print("\nResponse copied to clipboard!")
            except:
                print("\nCould not copy to clipboard")
        else:
            print("No valid response received or automation was detected")
            print(f"Response: {response_text}")
        print("=" * 60)
        
        # Human-like pause before closing
        time.sleep(random.uniform(4, 8))
        
    except Exception as e:
        print(f"Error in iteration {iteration}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
                print(f"Browser closed for iteration {iteration}")
            except:
                pass

def run_automation():
    """
    Run the automation 5 times with advanced anti-detection
    """
    print("Starting Advanced Anti-Detection ChatGPT Automation - 5 iterations")
    print("Using undetected-chromedriver for maximum stealth")
    
    for i in range(1, 6):
        try:
            automated_chatgpt_query(i)
            
            if i < 5:
                # Extended wait between iterations to avoid rate limiting
                wait_time = random.uniform(30, 60)
                print(f"\nWaiting {wait_time:.1f} seconds before next iteration (anti-detection delay)...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print(f"\nAutomation interrupted by user at iteration {i}")
            break
        except Exception as e:
            print(f"Error in iteration {i}: {e}")
            # Wait before retry
            time.sleep(random.uniform(15, 30))
            continue
    
    print("\n=== AUTOMATION COMPLETED ===")

if __name__ == "__main__":
    run_automation()
