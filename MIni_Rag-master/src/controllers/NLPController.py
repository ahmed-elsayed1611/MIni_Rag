from controllers.BaseController import BaseController
from models.db_schemes import project, data_chunck
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

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self,project: project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        self.vector_db_client.delete_collection(collection_name)

    def get_vector_db_collection_info(self,project: project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        try:
            collection_info = self.vector_db_client.get_collection_info(collection_name)
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

    def index_into_vector_db(self,project: project , chunks: List[data_chunck],do_reset :bool = False,chunck_id: Optional[List[int]] = None):

        # Get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        # manage items

        texts = [c.chunck_text for c in chunks]
        metadata = [c.chunck_meta_data for c in chunks]

        if hasattr(self.embedding_client, "embed_texts"):
            Vectors = self.embedding_client.embed_texts(texts=texts, document_type=DocumentTypeEnums.DOCUMENT.value)
        else:
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
        try:
            results = self.vector_db_client.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)
        except Exception:
            # Collection does not exist or other provider error
            return False

        if not results or len(results) == 0:
            return False
    
        return results

    async def answer_rag_question(self, project: project, query: str, limit: int = 10):
    
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = self.search_vector_db_collection(
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

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history

