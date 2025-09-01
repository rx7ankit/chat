from fastapi import FastAPI
from pydantic import BaseModel
from script import get_chatgpt_response

app = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
