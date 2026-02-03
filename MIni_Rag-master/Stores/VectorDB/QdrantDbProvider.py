from qdrant_client import QdrantClient, models
from .Providers.VectorDBInterface import VectorDBInterface
from .Providers.VectoDBEnums import VectorDBEnums, DistancMethodEnums
import logging
from models.db_schemes import RetrievedDocument

class QdrantDb(VectorDBInterface):

    def __init__(self, Db_path: str = None, distance_method: str = None, db_client: str = None, default_vector_size: int = None, index_threshold: int = None, **kwargs):
        self.client = None
        self.db_path = Db_path if Db_path is not None else db_client
        self.distance_method = distance_method
        self.logger = logging.getLogger(__name__)

        if self.distance_method == "cosine":
            self.distance_method = models.Distance.COSINE
        elif self.distance_method == "dot":
            self.distance_method = models.Distance.DOT
        else:
            self.logger.warning("Invalid distance method")

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        return None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def list_all_collections(self) -> list:
        collections = self.client.get_collections()
        return collections.collections if collections else []

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            result = self.client.delete_collection(collection_name=collection_name)
            return result
        else:
            self.logger.warning("Collection does not exist")

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            self.delete_collection(collection_name=collection_name)
        if not self.is_collection_existed(collection_name):
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

    def insert_one(self, collection_name: str, text: str, vector: list,
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

    def insert_many(self, collection_name: str, texts: list,
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

    def insert(self, collection_name: str, documents: list, metadatas: list, vectors: list, record_ids: list = None):
        return self.insert_many(collection_name=collection_name, texts=documents, vectors=vectors, metadata=metadatas, record_ids=record_ids)

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):

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
