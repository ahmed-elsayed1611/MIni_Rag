from fastapi import APIRouter, Depends, File, UploadFile
from src.helpers.config import get_settings, Settings
from src.controlers import DataController, ProjectControllers
from src.models import ResponseStatus
import aiofiles
import os

data_router = APIRouter(
    prefix="/data",
    tags=["data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: int,
    file: UploadFile = File(..., description="File to upload"),
    app_settings: Settings = Depends(get_settings),
):
    result_signal = DataController().validate_upload_file(file=file)
    if result_signal != ResponseStatus.File_Upload_success:
        return {"signal": result_signal.value}
    
    project_dir_path = ProjectControllers().get_project_path(project_id=project_id)
    file_path = os.path.join(project_dir_path, file.filename) 

    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)
    
    return {"signal": f"File uploaded successfully to {file_path}"}