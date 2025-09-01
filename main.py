from fastapi import FastAPI
from pydantic import BaseModel
from script import get_chatgpt_response
import asyncio
import concurrent.futures
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    logger.info(f"Starting parallel request {request_id} for message: {request.message[:50]}...")
    
    try:
        # Run the Chrome automation in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor, 
            get_chatgpt_response, 
            request.message
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Request {request_id} completed in {processing_time:.2f} seconds")
        
        return ChatResponse(
            response=response,
            request_id=request_id,
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error: {str(e)}"
        logger.error(f"Request {request_id} failed after {processing_time:.2f} seconds: {error_msg}")
        
        return ChatResponse(
            response=error_msg,
            request_id=request_id,
            processing_time=processing_time
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the thread pool executor on shutdown"""
    logger.info("Shutting down thread pool executor...")
    executor.shutdown(wait=True)
