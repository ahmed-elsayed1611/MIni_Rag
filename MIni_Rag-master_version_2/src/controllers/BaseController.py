from helpers.config import get_settings
import os
import random
import string



class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_directory = os.path.join(self.base_directory, "assets", "files")
        self.database_dir = os.path.join(self.base_directory, "assets", "database")

    def generate_unique_filename(self, length: int = 8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))  

    def get_database_path(self,db_name: str):
        if not os.path.exists(self.database_dir):
            os.makedirs(self.database_dir)
        return os.path.join(self.database_dir, db_name)
