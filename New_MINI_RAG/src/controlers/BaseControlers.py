import os
from src.helpers.config import get_settings, Settings
import random
import string
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.file_dir = "uploads"  # Default upload directory

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename to avoid conflicts."""
        name, ext = os.path.splitext(original_filename)
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"{name}_{random_suffix}{ext}"


