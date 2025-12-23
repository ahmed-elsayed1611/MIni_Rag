from fastapi import APIRouter, UploadFile, Depends, Request
from src.helpers.config import get_settings, Settings
from src.controlers import DataController

data_router = APIRouter(
    prefix="/data",
    tags=["data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: int, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):

    is_valid =  DataController().validate_upload_file(file=file)
    return is_valid