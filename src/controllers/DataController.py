from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus


class DataController(BaseController):
    
    def __init__(self):
        super().__init__()

    def Validate_Uploaded_Files(self ,file : UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseStatus.INVALID_FILE_TYPE.value
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, ResponseStatus.FILE_TOO_LARGE.value
        return True, ResponseStatus.SUCCESS.value
