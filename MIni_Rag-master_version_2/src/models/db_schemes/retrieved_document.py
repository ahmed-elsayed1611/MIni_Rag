from pydantic import BaseModel
from typing import Optional


class RetrievedDocument(BaseModel):
    score: Optional[float] = None
    text: str
    chunk_id: Optional[int] = None
    asset_id: Optional[int] = None
    metadata: Optional[dict] = None
