#!/usr/bin/env python3
"""
Start the parallel ChatGPT scraping server
"""
import uvicorn
import sys
import os

def main():    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,  # Keep as 1 since we handle parallelism within the app
        log_level="warning",  # Reduced logging to only show warnings/errors
        access_log=False  # Disable access logs for cleaner output
    )

if __name__ == "__main__":
    main()
