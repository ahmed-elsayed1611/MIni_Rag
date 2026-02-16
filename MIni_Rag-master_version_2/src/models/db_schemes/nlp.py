from pydantic import BaseModel 
from typing import Optional

class PushRequest(BaseModel): 
    do_reset: Optional[int] = 0
    page_no: Optional[int] = 1
    page_size: Optional[int] = 50

class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 10