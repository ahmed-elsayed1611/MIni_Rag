from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
   
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
