from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    total_chunks: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
