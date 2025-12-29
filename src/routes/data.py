from fastapi import APIRouter, Depends, UploadFile, HTTPException , status
from helpers import get_settings ,settings
from controllers import DataController , ProjectController
from models import ResponseStatus
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(

    prefix = "/AI/data"
)

@data_router.post("/{project_id}")
async def get_data(project_id: str, file: UploadFile, app_settings: settings = Depends(get_settings)):
    is_valid, error_status = DataController().Validate_Uploaded_Files(file=file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"status": error_status})
    if is_valid:
        project_controller = ProjectController()
        project_dir_path = project_controller.get_project_path(project_id=project_id)
        file_path = DataController().generate_unique_filename(file.filename, project_id)    
        # Save the file chunk by chunk
        try:
            async with aiofiles.open(file_path ,'wb') as f :
                while chunk := await file.read(int(app_settings.FILE_DEFUALT_CHUNCK_SIZE)):
                    await f.write(chunk)
        except Exception as e:
            logger.error(f"Error saving file: {e}")

            print(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'signal': ResponseStatus.SUCCESS.value
            }
        )


    
