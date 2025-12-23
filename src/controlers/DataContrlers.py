from .BaseControlers import BaseController
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from src.models import ResponseStatus

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_upload_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            raise ResponseStatus.File_Type_Not_Accepted
            
        # Get file size by seeking to the end
        file.file.seek(0, 2)  # 2 means seek to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer
        
        if file_size > self.app_settings.FILE_MAX_SIZE * 1024 * 1024:
            raise ResponseStatus.File_Size_Too_Large
            
        return ResponseStatus.File_Upload_success

