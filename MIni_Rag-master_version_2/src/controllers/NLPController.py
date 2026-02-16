from controllers.BaseController import BaseController
from models.db_schemes.Mini_rag.schemes import Project, DataChunk
from Stores.llm.LLMEnums import DocumentTypeEnums
from typing import List, Optional
import json

class NLPController(BaseController):

    def __init__(self,vector_db_client,embedding_client,generation_client,template_parser):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    async def create_collection_name(self, project_id: str):
        return f"collection_{self.vector_db_client.default_vector_size}_{project_id}".strip()
    

    async def reset_vector_db_collection(self,project: Project):
        collection_name = await self.create_collection_name(project_id=project.id)
        await self.vector_db_client.delete_collection(collection_name)

    async def get_vector_db_collection_info(self,project: Project):
        collection_name = await self.create_collection_name(project_id=project.id)
        try:
            collection_info =await self.vector_db_client.get_collection_info(collection_name)
        except Exception:
            # Collection does not exist or other provider error; return a simple fallback
            return {"collection_name": collection_name, "status": "not_found"}

        if hasattr(collection_info, "model_dump"):
            return collection_info.model_dump()
        if hasattr(collection_info, "dict"):
            return collection_info.dict()
        if hasattr(collection_info, "__dict__"):
            return collection_info.__dict__
        return collection_info

    async def index_into_vector_db(self,project: Project , chunks: List[DataChunk],do_reset :bool = False,chunck_id: Optional[List[int]] = None):

        # Get collection name
        collection_name = await self.create_collection_name(project_id=project.id)
        # manage items

        texts = [c.chunk_text for c in chunks]
        metadata = [
            {
                **(c.chunk_metadata or {}),
                "asset_id": c.chunk_asset_id,
                "project_id": c.chunk_project_id,
                "chunk_db_id": c.id,
            }
            for c in chunks
        ]

        if chunck_id is None:
            chunck_id = [c.id for c in chunks]

        if hasattr(self.embedding_client, "embed_texts"):
            Vectors = self.embedding_client.embed_texts(texts=texts, document_type=DocumentTypeEnums.DOCUMENT.value)
        else:
            Vectors = [self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnums.DOCUMENT.value) for text in texts]

        #create collection if not exists
        await self.vector_db_client.create_collection(collection_name=collection_name,embedding_size = self.embedding_client.embedding_size,do_reset = do_reset)
        
        #insert into vector database
        await self.vector_db_client.insert_many(collection_name=collection_name,texts=texts,vectors=Vectors,metadata=metadata,record_ids=chunck_id)

        return True
    
    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # step1: get collection name
        query_vector = None
        collection_name = await self.create_collection_name(project_id=project.id)

        # step2: get text embedding vector
        vectors = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnums.QUERY.value)

        if not vectors or len(vectors) == 0:
            return False
        
        # Handle different vector formats from embedding client
        if isinstance(vectors, list):
            if len(vectors) > 0:
                query_vector = vectors[0] if isinstance(vectors[0], list) else vectors
            else:
                return False
        else:
            query_vector = vectors

        if not query_vector or not isinstance(query_vector, (list, tuple)):
            return False    

        # step3: do semantic search
        results = await self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        if not results:
            return False

        return results


    async def answer_rag_question(self, project: Project, query: str, limit: int = 10):
    
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])
        chat_history.append(self.generation_client.construct_prompt(
            prompt=full_prompt,
            role=self.generation_client.enums.USER.value,
        ))

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history



#docker compose up pgvector
#docker compose down