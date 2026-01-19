from fastapi import APIRouter, Depends, UploadFile, HTTPException , status
from helpers import get_settings ,settings
from controllers import DataController , ProjectController
from controllers.ProcessController import ProcessController
from models import ResponseStatus
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
import json
from routes.schemes.data import ProcessRequest

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(

    prefix = "/AI/data"
)

@data_router.post("/upload/{project_id}")
async def get_data(project_id: str, file: UploadFile, app_settings: settings = Depends(get_settings)):
    is_valid, error_status = DataController().Validate_Uploaded_Files(file=file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"status": error_status})
    if is_valid:
        project_controller = ProjectController()
        project_dir_path = project_controller.get_project_path(project_id=project_id)
        file_path,file_id = DataController().generate_unique_filepath(file.filename, project_id)    
        # Save the file chunk by chunk
        try:
            async with aiofiles.open(file_path ,'wb') as f :
                while chunk := await file.read(int(app_settings.FILE_DEFUALT_CHUNCK_SIZE)):
                    await f.write(chunk)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        return JSONResponse(
            content={
                'signal': ResponseStatus.SUCCESS.value,
                'file_id' : file_id
            }
        )


    
@data_router.post("/process/{project_id}")
async def process_data(project_id: str, ProcessRequest: ProcessRequest, app_settings: settings = Depends(get_settings)):
    
    file_id = ProcessRequest.file_id
    chunk_size = ProcessRequest.chunk_size
    overlap = ProcessRequest.overlap_size

    
    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)

    file_chuncks = process_controller.process_file_content(file_content=file_content,
                                                                chunk_size=chunk_size, 
                                                                chunk_overlap=overlap)


    if file_chuncks is not None:
        return JSONResponse(
            content={
                'signal': ResponseStatus.SUCCESS.value,
                'file_id' : file_id,
                'file_chuncks' : file_chuncks
                }
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'signal': ResponseStatus.ERROR.value,
                'file_id' : file_id,
                'error' : "Failed to process file"
            }
        )
            
