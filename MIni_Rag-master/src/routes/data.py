from fastapi import APIRouter, Depends, UploadFile, HTTPException , status ,Request
from helpers import get_settings ,settings
from controllers import DataController , ProjectController
from controllers.ProcessController import ProcessController
from models import ResponseStatus
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
import json
from .schemes.data import ProcessRequest
from models.ProjecModel import ProjectModel
from models.db_schemes.data_chunck import data_chunck
from models.ChunckModel import ChunckModel


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(

    prefix = "/AI/data"
)

@data_router.post("/upload/{project_id}")
async def get_data(request:Request,project_id: str, file: UploadFile, app_settings: settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(db_client=request.app.db)
    project_obj = await project_model.get_project_or_create_one(project_id=project_id)

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
                'file_id' : file_id,
            }
        )


    
@data_router.post("/process/{project_id}")
async def process_data(request:Request,project_id: str, ProcessRequest: ProcessRequest, app_settings: settings = Depends(get_settings)):
    
    file_id = ProcessRequest.file_id
    chunk_size = ProcessRequest.chunk_size
    overlap = ProcessRequest.overlap_size
    do_reset = ProcessRequest.do_reset
    
    

    project_model = await ProjectModel.create_instance(db_client=request.app.db)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    chunck_model =await ChunckModel.create_instance(db_client=request.app.db)
    
    # Reset functionality: delete existing chunks if do_reset == 1
    if do_reset == 1:
        deleted_count = await chunck_model.delete_chuncks_by_project_id(project_id=project['_id'])
        logger.info(f"Reset: Deleted {deleted_count} existing chunks for project {project_id}")
    
    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)

    file_chuncks = process_controller.process_file_content(file_content=file_content,
                                                                chunk_size=chunk_size, 
                                                                chunk_overlap=overlap)

    no_records = 0
    if file_chuncks is not None:
        file_chuncks_record = [
            data_chunck (
                chunck_text = chunc['page_content'],
                chunck_meta_data = chunc['metadata'],
                chunck_order = i+1,
                chunck_project_id = project['_id']
            )
            for i , chunc in enumerate(file_chuncks)
        ]
        
        no_records = await chunck_model.insert_many_chuncks(chuncks=file_chuncks_record)
      
    return JSONResponse(
        content={
            'signal': ResponseStatus.SUCCESS.value,
            'no_records' : no_records
            }
        )