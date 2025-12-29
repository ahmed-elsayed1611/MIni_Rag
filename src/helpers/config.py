from pydantic_settings import BaseSettings 

class settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_MAX_SIZE: int
    FILE_ALLOWED_TYPES: str
    FILE_DEFUALT_CHUNCK_SIZE: int

 
    class Config:
        env_file = ".env"
      
def get_settings():
    return settings()