from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
   
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[1] / ".env")
    )

def get_settings():
    return Settings()
