#!/usr/bin/env python3
"""
Simple test for browser creation without reuse issues
"""
import undetected_chromedriver as uc
import tempfile
import os
import time
import random
from selenium.webdriver.common.by import By

def create_simple_headless_browser():
    """Create a simple headless browser without complex options"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="chrome_test_")
        user_data_dir = os.path.join(temp_dir, "user_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Simple options
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Create driver
        driver = uc.Chrome(
            options=options,
            version_main=None,
            use_subprocess=False
        )
        
        return driver, temp_dir
        
    except Exception as e:
        print(f"Error creating browser: {e}")
        return None, None

def test_simple_headless():
    """Test simple headless browser creation"""
    print("🧪 Testing simple headless browser...")
    
    driver, temp_dir = create_simple_headless_browser()
    
    if not driver:
        print("❌ Failed to create browser")
        return False
    
    try:
        print("✅ Browser created successfully!")
        
        # Test navigation
        print("🌐 Testing navigation to Google...")
        driver.get("https://www.google.com")
        time.sleep(3)
        
        title = driver.title
        print(f"📄 Title: {title}")
        
        if "Google" in title:
            print("✅ Simple headless test passed!")
            return True
        else:
            print("❌ Navigation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("🧹 Browser closed")
            except:
                pass
        
        # Cleanup temp directory
        if temp_dir:
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

if __name__ == "__main__":
    success = test_simple_headless()
    if success:
        print("\n🎉 Simple headless test passed!")
    else:
        print("\n💥 Simple headless test failed!")
    
    exit(0 if success else 1)
