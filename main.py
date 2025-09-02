from fastapi import FastAPI
from pydantic import BaseModel
from script import get_chatgpt_response
import asyncio
import concurrent.futures
import time

app = FastAPI()


# MAXIMUM PARALLELISM - No limits!
MAX_WORKERS = 500  # Increased to 500 for true parallelism
executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

@app.get("/")
async def root():
    return {"message": "FastAPI server running with MAXIMUM parallelism!"}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    processing_time: float = None

@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.time()
    
    try:
        # Run in executor with maximum parallelism
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor, 
            get_chatgpt_response, 
            request.message
        )
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=response,
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error: {str(e)}"
        
        return ChatResponse(
            response=error_msg,
            processing_time=processing_time
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the thread pool executor on shutdown"""
    executor.shutdown(wait=True)
