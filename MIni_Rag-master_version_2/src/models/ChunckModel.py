from .BaseDataModel import BaseDataModel
from .db_schemes.Mini_rag.schemes import DataChunk
from .Enums.DataBaseEnums import DataBasesEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from sqlalchemy import select, func, delete

class ChunckModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance



    async def create_chunck(self, chunck: DataChunk):
         async with self.db_client() as session:
            async with session.begin():
                session.add(chunck)
            await session.refresh(chunck)
            return chunck
       
    async def get_chuncks(self, chunck_id: str):
         async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(select(DataChunk).where(DataChunk.id == chunck_id))
                return result.scalar_one_or_none()



    async def insert_many_chuncks(self, chuncks: list, batch_size: int = 100):
        async with self.db_client() as session:
            async with session.begin():
                for chunck in chuncks:
                    session.add(chunck)
                return len(chuncks)

    async def get_total_chunks_count(self, project_id: ObjectId):
        total_count = 0
        async with self.db_client() as session:
            count_sql = select(func.count(DataChunk.id)).where(DataChunk.chunk_project_id == project_id)
            records_count = await session.execute(count_sql)
            total_count = records_count.scalar()
        
        return total_count




    async def delete_chuncks_by_project_id(self, project_id: ObjectId):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(delete(DataChunk).where(DataChunk.chunk_project_id == project_id))
                return result.rowcount

    async def get_poject_chunks(self, project_id: ObjectId, page_no: int = 1, page_size: int = 50):
        async with self.db_client() as session:
            async with session.begin():
                total_result = await session.execute(select(func.count(DataChunk.id)).where(DataChunk.chunk_project_id == project_id))
                total_result = total_result.scalar_one()
                skip_count = (page_no - 1) * page_size
                result = await session.execute(select(DataChunk).where(DataChunk.chunk_project_id == project_id).order_by(DataChunk.chunk_order).offset(skip_count).limit(page_size))
                chunks = result.scalars().all()
                return chunks, total_result

