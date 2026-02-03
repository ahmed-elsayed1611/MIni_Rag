from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "qdrant"
    PGVECTOR = "pgvector"

class DistancMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"