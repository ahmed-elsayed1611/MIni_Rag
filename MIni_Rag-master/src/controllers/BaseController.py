from helpers.config import get_settings
import os
import random
import string



class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_directory = os.path.join(self.base_directory, "assets", "files")

    def generate_unique_filename(self, length: int = 8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))  

    
    
