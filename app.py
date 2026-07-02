from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List

from conversation_manager import handle_chat


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors and errors[0].get("type") == "json_invalid":
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid JSON body. Use valid JSON with straight quotes. Example: {\"messages\":[{\"role\":\"user\",\"content\":\"Hiring a Java developer...\"}]}.",
            },
        )
    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/")
def root():
    return {
        "message": "Use GET /health and POST /chat with valid JSON. POST /chat body schema: {\"messages\":[{\"role\":\"user\",\"content\":\"...\"}]}.",
    }


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class RecommendationItem(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    end_of_conversation: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in request.messages
    ]
    return handle_chat(messages)