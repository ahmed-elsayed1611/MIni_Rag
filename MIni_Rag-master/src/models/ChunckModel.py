from .BaseDataModel import BaseDataModel
from .db_schemes.data_chunck import data_chunck
from .Enums.DataBaseEnums import DataBasesEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
class ChunckModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBasesEnum.Collection_DataChuncks_name.value]
    
    async def create_chunck(self, chunck: data_chunck):
        result =  await self.collection.insert_one(chunck.dict(by_alias=True,exclude_unset=True))
        chunck._id = result.inserted_id
        return chunck

    async def get_chuncks(self, chunck_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunck_id)})
        if result:
            return data_chunck(**result)
        else:
            return None
    
    async def insert_many_chuncks(self, chuncks: list,batch_size: int = 100):
        for i in range(0, len(chuncks), batch_size):
            batch = chuncks[i:i + batch_size]
            operations = [
                InsertOne(chunck.dict(by_alias=True,exclude_unset=True))
                for chunck in batch
            ]
            await self.collection.bulk_write(operations)
        return len(chuncks)

    async def delete_chuncks_by_project_id(self, project_id: ObjectId):
      result= await self.collection.delete_many({"chunck_project_id": project_id})
      return result.deleted_count