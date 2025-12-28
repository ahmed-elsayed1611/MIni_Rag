from fastapi import APIRouter, Depends, UploadFile, HTTPException , status
from helpers import get_settings ,settings
from controllers import DataController
from models import ResponseStatus
from fastapi.responses import JSONResponse


data_router = APIRouter(

    prefix = "/AI/data"
)

@data_router.post("/{project_id}")
async def get_data(project_id: str, file: UploadFile, app_settings: settings = Depends(get_settings)):
    is_valid, error_status = DataController().Validate_Uploaded_Files(file=file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"status": error_status})
    if is_valid:
        # Process the valid file here
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": error_status, "filename": file.filename})