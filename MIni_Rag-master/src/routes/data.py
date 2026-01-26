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
from models.AssetModel import AssetModel
from models.db_schemes.asset import Asset 
from models.Enums.AssetTypeEnum import AssetTypeEnum

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

        # store the assets to the DB 
        asset_model = await AssetModel.create_instance(db_client=request.app.db) 
        asset_resource =  Asset(
            asset_project_id = project_obj.id,
            asset_type= AssetTypeEnum.FILE.value,
            asset_name = file_id,
            asset_size = os.path.getsize(file_path),
            asset_path = file_path
        )

        asset_record = await asset_model.create_asset(asset=asset_resource)


        return JSONResponse(
            content={
                'signal': ResponseStatus.SUCCESS.value,
                'file_id' : file_id,
                'asset_id' : str(asset_record.id)
            }
        )


    
@data_router.post("/process/{project_id}")
async def process_data(request:Request,project_id: str, ProcessRequest: ProcessRequest, app_settings: settings = Depends(get_settings)):
    
    chunk_size = ProcessRequest.chunk_size
    overlap = ProcessRequest.overlap_size
    do_reset = ProcessRequest.do_reset
    
    

    project_model = await ProjectModel.create_instance(db_client=request.app.db)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    asset_model = await AssetModel.create_instance(db_client=request.app.db)

    project_files_ids = {}
    if ProcessRequest.file_id:
        asset_record = await asset_model.get_asset_record(asset_project_id=project.id, asset_name=ProcessRequest.file_id)

        if not asset_record:
            return JSONResponse(
                content={
                    'signal': ResponseStatus.ERROR.value,
                    'status': 'File not found'
                }
            )

        project_files_ids = {asset_record.id: asset_record.asset_name}

    else:
       project_files = await asset_model.get_all_project_assets(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value
       )
       project_files_ids = { record.id: record.asset_name for record in project_files}

    if len(project_files_ids) == 0:
       
       return JSONResponse(
           content={
               'signal': ResponseStatus.ERROR.value,
               'status': 'No files found for this project'
           }
       )
       
    chunck_model =await ChunckModel.create_instance(db_client=request.app.db)
    
    
    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    # Reset functionality: delete existing chunks if do_reset == 1
    if do_reset == 1:
        deleted_count = await chunck_model.delete_chuncks_by_project_id(project_id=project.id)
        logger.info(f"Reset: Deleted {deleted_count} existing chunks for project {project_id}")
    


    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)
       
        if file_content is None:
            logger.warning(f"File {file_id} not found or could not be loaded")
            continue
      
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
                    chunck_project_id = project.id,
                    chunck_asset_id = asset_id
                )
                for i , chunc in enumerate(file_chuncks)
            ]
            
            no_records = await chunck_model.insert_many_chuncks(chuncks=file_chuncks_record)
        
        no_files += 1
    
    return JSONResponse(
        content={
            'signal': ResponseStatus.SUCCESS.value,
            'no_records' : no_records,
            'proceesed_files' : no_files
            }
    )