from fastapi import FastAPI
from pydantic import BaseModel
from script import get_chatgpt_response

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI server is running!"}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Use script.py to get ChatGPT response
        response = get_chatgpt_response(request.message)
        return ChatResponse(response=response)
    
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}")
