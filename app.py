import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from utils import load_all_chats, get_chat, save_chat, generate_ai_response, get_stats

MM_INSTRUCTION_PROMPT = """
    You are the control LLM. 
    Your task is to split the following code into up to 3 separate tasks.
    Write each task as a clear, unambiguous instruction. 
    Each task must be self-contained and should not require information from the other tasks to be completed.
    Do keep in mind that you will have to reassemble the final answer from the 3 smaller parts, so try to split in a way that makes it easy to reassemble.
    Do not provide any features that are not explicitly requested in the original user message.
    Do not make up any functions without explaining how they work with code.
    Split the tasks with a newline character. Do not add anything else in your response.
    The code to split is: """

app = FastAPI(title="FastAPI Ollama Chat")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

class MessageRequest(BaseModel):
    content: str
    title: str | None = None


def build_model_messages(messages: list[dict]) -> list[dict]:
    model_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            model_messages.append({
                "role": "user",
                "content": MM_INSTRUCTION_PROMPT + msg.get("content", "")
            })
        else:
            model_messages.append(msg)
    return model_messages

@app.get("/")
async def root(request: Request):
    chats = load_all_chats()

    if os.name == 'posix':
        return templates.TemplateResponse(
            request=request, 
            name="chat.html", 
            context={"chats": chats}
        )
    else:
        return templates.TemplateResponse(
            request=request, 
            name="chat.html", 
            context={"chats": chats}
        )

@app.get("/chat/{chat_id}")
async def get_chat_history(chat_id: str):
    chat_data = get_chat(chat_id)
    if chat_data is None:
        return JSONResponse(status_code=404, content={"message": "Chat not found"})
    return chat_data

@app.post("/chat/{chat_id}/message")
async def send_message(chat_id: str, message: MessageRequest):
    chat_data = get_chat(chat_id) or {"id": chat_id, "messages": []}
    
    if message.title:
        chat_data["title"] = message.title

    chat_data["messages"].append({"role": "user", "content": message.content})
    ai_content, eval_count = await generate_ai_response(build_model_messages(chat_data["messages"]))
    chat_data["messages"].append({"role": "assistant", "content": ai_content})
    chat_data["tokens_used"] = chat_data.get("tokens_used", 0) + eval_count
    
    save_chat(chat_id, chat_data)
    
    
    return {"role": "assistant", "content": ai_content}

@app.get("/stats")
async def stats():
    return get_stats()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5010, reload=True)