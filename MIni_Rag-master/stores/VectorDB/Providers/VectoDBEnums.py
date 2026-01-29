from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "qdrant"

class DistancMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
    