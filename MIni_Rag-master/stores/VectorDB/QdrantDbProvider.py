from qdrant_client import QdrantClient , models
from .Providers.VectorDBInterface import VectorDBInterface
from .Providers.VectoDBEnums import VectorDBEnums, DistancMethodEnums
import logging

class QdrantDb(VectorDBInterface):

    def __init__(self,Db_path: str , distance_method: str):
        self.client = None
        self.db_path = Db_path
        self.distance_method = distance_method
        
        if self.distance_method == "cosine":
            self.distance_method = models.Distance.COSINE
        elif self.distance_method == "dot":
            self.distance_method = models.Distance.DOT
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.warning("Invalid distance method")

        
    async def connect(self):
        self.client = QdrantClient(path=self.db_path)
        
    async def disconnect(self):
        raise NotImplementedError("disconnect method is not implemented for QdrantDb")
    
    async def is_collection_existed(self,collection_name: str) -> bool:
       return self.client.collection_exists(collection_name)
    async def list_all_collections(self) -> list:
       return self.client.list_all_collections()
    async def get_collection_info(self,collection_name: str) -> dict:
       return self.client.get_collection(collection_name)
    async def delete_collection(self,collection_name: str):
        if await self.is_collection_existed(collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            result = self.client.delete_collection(collection_name=collection_name)
            return result
        else:
            self.logger.warning("Collection does not exist")
            
    async def create_collection(self,collection_name:str,embedding_size:int,do_reset:bool=False):
        if do_reset:
            await self.delete_collection(collection_name=collection_name)
        if not await self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            self.logger.info(f"Collection {collection_name} created successfully")
        else:
            self.logger.info(f"Collection {collection_name} already exists")
            
        return True

    
    async def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False
        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
            return True
        except Exception as e:
            self.logger.error(f"Error inserting record: {e}")
            return False


    async def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50):
        
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadata[x]
                    }
                )

                for x in range(len(batch_texts))
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True
        
    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):

        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results or len(results) == 0:
            return None
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"],
            })
            for result in results
        ]

