from pydantic_settings import BaseSettings 
import os
from typing import Optional

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_FILE = os.path.join(_BASE_DIR, ".env")

class settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_MAX_SIZE: int
    FILE_ALLOWED_TYPES: str
    FILE_DEFUALT_CHUNCK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    OPENAI_API_URL: str = ''
    COHERE_API_KEY: str = ''
    GROQ_API_KEY: str = ''
    GROQ_API_URL: str = ''
    
    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int
    
    default_input_max_characters: int = 1024
    default_generation_max_output_tokens: int = 200
    default_generation_temperature: float = 0.1


    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = None
     
 
    class Config:
        env_file = _ENV_FILE
      
def get_settings():
    return settings()