from ..QdrantDbProvider import QdrantDb as QdrantDBProvider
from .VectoDBEnums import VectorDBEnums
from controllers.BaseController import BaseController
from typing import Any


class VectorDBProviderFactory(BaseController):

    def __init__(self,config: Any, db_client: Any = None):
        super().__init__()
        self.config = config
        self.base_controller = BaseController()
        self.db_client =db_client

    def _get_config_value(self, key: str, default: Any = None):
        if isinstance(self.config, dict):
            return self.config.get(key, default)
        return getattr(self.config, key, default)

    def create(self, provider: str):
        if isinstance(provider, str):
            provider = provider.strip().lower()
        if provider == VectorDBEnums.QDRANT.value.lower():
            qdrant_db_client = self.base_controller.get_database_path(db_name=self._get_config_value("VECTOR_DB_PATH"))

            return QdrantDBProvider(
                db_client=qdrant_db_client,
                distance_method=self._get_config_value("VECTOR_DB_DISTANCE_METHOD"),
                default_vector_size=self._get_config_value("EMBEDDING_MODEL_SIZE"),
                index_threshold=self._get_config_value("VECTOR_DB_PGVEC_INDEX_THRESHOLD"),
            )
        
        if provider == VectorDBEnums.PGVECTOR.value.lower():
            return None
        
        return None
