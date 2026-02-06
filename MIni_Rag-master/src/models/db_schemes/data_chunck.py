from pydantic import BaseModel , Field ,validator
from typing import Optional
from bson.objectid import ObjectId

class data_chunck(BaseModel):
    id :Optional[ObjectId] = Field(default=None,alias="_id")
    chunck_text : str = Field(..., min_length=1)
    chunck_meta_data : dict 
    chunck_order : int = Field(..., ge=1)
    chunck_project_id : ObjectId = Field(..., description="Project ID this chunk belongs to")
    chunck_asset_id : ObjectId
    class Config:
        arbitrary_types_allowed = True  



      
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunck_project_id",1)],
                "name": "chunck_project_id_index_1",
                "unique": False
            }
        ]



class RetrivedChunk(BaseModel):
    text: str
    score: float




 