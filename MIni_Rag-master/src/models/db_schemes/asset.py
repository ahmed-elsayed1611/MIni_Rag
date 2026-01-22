from pydantic import BaseModel , Field ,validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id :Optional[ObjectId] = Field(default=None,alias="_id")
    asset_project_id : ObjectId = Field(..., description="Project ID this asset belongs to")
    asset_name : str = Field(..., min_length=1)
    asset_type : str = Field(..., min_length=1)
    asset_size : Optional[int] = Field(None, ge=1)
    asset_config : Optional[dict] = Field(None)
    asset_pushed_at : datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True  

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_project_id",1)],
                "name": "asset_project_id_index_1",
                "unique": False
            },
            {
                "key": [
                    ("asset_name",1),
                    ("asset_project_id",1)
                ],
                "name": "asset_name_project_id_index_1",
                "unique": True
            }
        ] 

