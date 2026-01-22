from .BaseDataModel import BaseDataModel
from .db_schemes.data_chunck import data_chunck
from .Enums.DataBaseEnums import DataBasesEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from .db_schemes.asset import Asset

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBasesEnum.Collection_Assets_name.value]

    @classmethod
    async def create_instance(cls,db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBasesEnum.Collection_Assets_name.value not in all_collections:
            self.collection = self.db_client[DataBasesEnum.Collection_Assets_name.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"],name=index["name"],unique=index["unique"])

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True,exclude_unset=True))
        asset._id = result.inserted_id
        return asset

    async def get_all_project_assets(self, asset_type_id: ObjectId):
        cursor = await self.collection.find({"asset_type_id": asset_type_id})
        assets = [Asset(**asset) for asset in await cursor.to_list(None)]
        return assets