from enum import Enum

class ResponseStatus(Enum):
    File_validate_success = "File validate successfully"
    File_validate_error = "File validate error"
    File_Type_Not_Accepted = "File type not accepted"
    File_Size_Too_Large = "File size too large"
    File_Upload_success = "File uploaded successfully"    

    