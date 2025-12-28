from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    INVALID_FILE = "invalid_file"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    INVALID_FILE_TYPE = "invalid_file_type"
    FILE_TOO_LARGE = "file_too_large"



