from pydantic import BaseModel
from typing import Optional


class RetrievedDocument(BaseModel):
    score: Optional[float] = None
    text: str
