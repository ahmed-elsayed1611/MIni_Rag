from .mini_rag_base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB 
from pydantic import BaseModel 


class DataChunk(Base):
    __tablename__ = "data_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid4, nullable=False)
    
    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_order = Column(Integer, nullable=False)

    chunk_created_at = Column(DateTime, default=func.now(), nullable=False)
    chunk_updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    chunk_project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    project = relationship("Project", back_populates="data_chunks")
    asset = relationship("Asset", back_populates="data_chunks")
    
    __table_args__ = (
        Index('ix_data_chunks_project_id', 'id'),
        Index('ix_data_chunks_uuid', 'uuid'),
    )



class RetrivedChunk(BaseModel):
    text: str
    score: float