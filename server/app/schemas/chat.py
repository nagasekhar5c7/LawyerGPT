from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-5.5"
