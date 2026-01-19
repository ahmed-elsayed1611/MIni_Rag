from pydantic import BaseModel , Field ,validator
from typing import Optional
from bson.objectid import ObjectId

class data_chunck(BaseModel):
    _id :Optional[ObjectId] 
    chunck_text : str = Field(..., min_length=1)
    chunck_meta_data : dict = 
    chunck_order : int = Field(..., min_length=1)
    



    











 class Config:
        arbitrary_types_allowed = True  