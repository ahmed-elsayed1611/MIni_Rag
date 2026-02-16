import os
from typing import List
from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from models.Enums.ProcessEmuns import ProcessingEnums
from dataclasses import dataclass 

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id: str):
        file_extension = self.get_file_extension(file_id)
        if file_extension == ".txt":
            return TextLoader(os.path.join(self.project_path, file_id))
        elif file_extension == ".pdf":
            return PyPDFLoader(os.path.join(self.project_path, file_id))
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        if not os.path.exists(file_path):
            return None
    
    def get_file_content(self,file_id:str):
        loader = self.get_file_loader(file_id)
        if loader is None:
            return None
        return loader.load()

    def process_file_content(self,file_content: list, chunk_size: int = 100, chunk_overlap: int = 20):

        file_content_text =[
            rec.page_content for rec in file_content
        ]
        
        file_content_metadata =[
            rec.metadata for rec in file_content
        ]

        # chunks = text_splitter.split_documents(file_content)
        

        chunks = self.process_simpler_splitter(file_content_text, file_content_metadata, chunk_size)
        
        # Convert Document objects to serializable format
        serializable_chunks = [
            {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]
        
        return serializable_chunks

    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag but preserve context
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 10 ]  # Increased minimum length

        chunks = []
        current_chunk = ""

        for line in lines:
            # Add line to current chunk
            if current_chunk:
                current_chunk += " " + line  # Use space instead of splitter_tag for better flow
            else:
                current_chunk = line
                
            # Check if we should create a chunk
            if len(current_chunk) >= chunk_size * 0.8:  # Create chunks at 80% of target size
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))
                current_chunk = ""

        # Add remaining content
        if len(current_chunk) > 50:  # Only add if substantial
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks

