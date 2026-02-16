from .mini_rag_base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB 
from pydantic import BaseModel 

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid4, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('ix_projects_uuid', 'uuid'),
    )
    
    data_chunks = relationship("DataChunk", back_populates="project")
    assets = relationship("Asset", back_populates="project")