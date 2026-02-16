from enum import Enum
from typing import Text

class VectorDBEnums(Enum):
    QDRANT = "qdrant"
    PGVECTOR = "pgvector"

class DistancMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"

class PgVectorTablesSchemeEnums(Enum):
    ID = 'id'
    TEXT = 'text'
    VECTOR = 'vector'
    CHUNK_ID = 'chunk_id'
    METADATA = 'metadata'
    _PREFIX = 'pgvector'


class PgVectorDistanceMethodEnums(Enum):
    COSINE = 'vector_cosine_ops'
    DOT = 'vector_12_ops'

class PgVectorIndexTypeEnums(Enum):
   HNSW = 'hnsw'
   IVFFLAT = 'ivfflat'
   