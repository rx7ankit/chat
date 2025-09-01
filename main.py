from fastapi import FastAPI
from pydantic import BaseModel
from script import get_chatgpt_response
import asyncio
import concurrent.futures
import time
import logging

# Set up logging - suppress unnecessary logs
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger(__name__)

# Suppress specific loggers that create noise
logging.getLogger("undetected_chromedriver").setLevel(logging.ERROR)
logging.getLogger("selenium").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

app = FastAPI()

# Global thread pool executor for parallel processing
MAX_WORKERS = 5  # Reduced for better stability - adjust based on your system capabilities
executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

@app.get("/")
async def root():
    return {"message": "FastAPI server is running with parallel processing!"}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    request_id: str = None
    processing_time: float = None

@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.time()
    request_id = f"req_{int(time.time() * 1000000)}"
    
    try:
        # Run the Chrome automation in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor, 
            get_chatgpt_response, 
            request.message
        )
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=response,
            request_id=request_id,
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error: {str(e)}"
        
        return ChatResponse(
            response=error_msg,
            request_id=request_id,
            processing_time=processing_time
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the thread pool executor on shutdown"""
    executor.shutdown(wait=True)
