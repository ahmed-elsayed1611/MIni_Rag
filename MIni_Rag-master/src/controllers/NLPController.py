import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.controllers.BaseController import BaseController
from src.models.db_schemes import project, data_chunck
from Stores.llm.LLMEnums import DocumentTypeEnums
from typing import List, Optional
import json

class NLPController(BaseController):

    def __init__(self,vector_db_client,embedding_client,generation_client):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self,project: project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        self.vector_db_client.delete_collection(collection_name)

    def get_vector_db_collection_info(self,project: project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name)
        if hasattr(collection_info, "model_dump"):
            return collection_info.model_dump()
        if hasattr(collection_info, "dict"):
            return collection_info.dict()
        if hasattr(collection_info, "__dict__"):
            return collection_info.__dict__
        return collection_info

    def index_into_vector_db(self,project: project , chunks: List[data_chunck],do_reset :bool = False,chunck_id: Optional[List[int]] = None):

        # Get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        # manage items

        texts = [c.chunck_text for c in chunks]
        metadata = [c.chunck_meta_data for c in chunks]

        Vectors = [self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnums.DOCUMENT.value) for text in texts]

        #create collection if not exists
        self.vector_db_client.create_collection(collection_name=collection_name,embedding_size = self.embedding_client.embedding_size,do_reset = do_reset)
        
        #insert into vector database
        self.vector_db_client.insert(collection_name=collection_name,documents=texts,metadatas=metadata,vectors=Vectors,record_ids=chunck_id)

        return True
    
    def search_vector_db_collection(self,project: project , text: str, limit: int = 10):
        #get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        #get_tect_embeding vector
        vector = self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnums.QUERY.value)
        if not vector or len(vector) == 0:
            return False
        #search
        results = self.vector_db_client.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)
        if not results or len(results) == 0:
            return False
        return results