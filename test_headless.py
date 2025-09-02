#!/usr/bin/env python3
"""
Test script to verify headless Chrome setup works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script import setup_undetected_browser_parallel
import time

def test_headless_browser():
    """Test if headless browser can be created and navigate to a simple page"""
    print("🧪 Testing headless browser setup...")
    
    driver = None
    try:
        # Test headless mode
        print("📱 Creating headless browser...")
        driver = setup_undetected_browser_parallel(headless=True)
        print("✅ Headless browser created successfully!")
        
        # Test navigation to a simple page
        print("🌐 Testing navigation to Google...")
        driver.get("https://www.google.com")
        
        # Wait a bit and check title
        time.sleep(3)
        title = driver.title
        print(f"📄 Page title: {title}")
        
        if "Google" in title:
            print("✅ Navigation test passed!")
            return True
        else:
            print("❌ Navigation test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("🧹 Browser closed successfully")
            except Exception as e:
                print(f"⚠️ Browser cleanup warning: {e}")

if __name__ == "__main__":
    success = test_headless_browser()
    if success:
        print("\n🎉 Headless browser test completed successfully!")
        print("Your automation should now work in headless mode.")
    else:
        print("\n💥 Headless browser test failed!")
        print("There may be issues with the headless configuration.")
    
    sys.exit(0 if success else 1)
