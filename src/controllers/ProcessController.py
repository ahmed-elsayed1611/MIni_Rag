import os
from .BaseController import BaseController
from controllers import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from models.Enums.ProcessEmuns import ProcessingEnums
from langchain.text_splitter import RecursiveCharacterTextSplitter


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
    
    def get_file_content(self,file_id:str):
        loader = self.get_file_loader(file_id)
        return loader.load()

    def process_file_content(self,file_content: list, chunk_size: int = 100, chunk_overlap: int = 20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)

        file_content_text =[
            rec.page_content for rec in file_content
        ]
        
        file_content_metadata =[
            rec.metadata for rec in file_content
        ]

        chunks = text_splitter.split_documents(file_content)
        
        # Convert Document objects to serializable format
        serializable_chunks = [
            {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]
        
        return serializable_chunks

