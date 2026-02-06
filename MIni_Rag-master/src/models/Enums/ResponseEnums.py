from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    INVALID_FILE = "invalid_file"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    INVALID_FILE_TYPE = "invalid_file_type"
    FILE_TOO_LARGE = "file_too_large"
    PROJECT_NOT_FOUND = "project_not_found"
    INSERT_INTO_VECTOR_DB_FAILED = "insert_into_vector_db_failed"
    INSERT_INTO_VECTOR_DB_SUCCESS = "insert_into_vector_db_success"
    VECTOR_DB_COLLECTION_RETRIVED = "vector_db_collection_retrived"
    VECTOR_DB_SEARCH_FAILED = "vector_db_search_failed"
    VECTORDB_SEARCH_SUCCESS = "vector_db_search_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCESS = "rag_answer_success"


