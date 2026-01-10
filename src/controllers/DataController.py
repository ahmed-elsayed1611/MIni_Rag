from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus
from .ProjectController import ProjectController
import re
import os



class DataController(BaseController):
    
    def __init__(self):
        super().__init__()

    def Validate_Uploaded_Files(self ,file : UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseStatus.INVALID_FILE_TYPE.value
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, ResponseStatus.FILE_TOO_LARGE.value
        return True, ResponseStatus.SUCCESS.value   
        
    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        random_string = super().generate_unique_filename()
        project_controller = ProjectController()
        project_path = project_controller.get_project_path(project_id)

        def get_clean_file_name(self, orig_file_name: str) -> str:
            # Remove special characters and spaces, keep only alphanumeric and dots
            return re.sub(r'[^a-zA-Z0-9.]', '_', orig_file_name)
        
        clean_name = get_clean_file_name(self, orig_file_name)
        unique_filename = f"{clean_name}_{random_string}"
        
        while os.path.exists(os.path.join(project_path, unique_filename)):
            random_string = super().generate_unique_filename()
            unique_filename = f"{clean_name}_{random_string}"
        
        # Return both the full path and the unique filename (file_id)
        return os.path.join(project_path, unique_filename), unique_filename