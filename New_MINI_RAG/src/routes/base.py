from fastapi import APIRouter
import os 



router = APIRouter(

    prefix="/AI/NLP",
    tags=["RAG"]
)

@router.get("/")
def welcome():
    app_name = os.getenv('APP_NAME')
    app_version = os.getenv('APP_VERSION')
    return {
        "app_name" : app_name,
        "app_version" : app_version,
        "message" : "Welcome to Mini-RAG"
    }