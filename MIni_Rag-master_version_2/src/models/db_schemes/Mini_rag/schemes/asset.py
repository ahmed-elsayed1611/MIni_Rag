from .mini_rag_base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB 
from pydantic import BaseModel 


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid4, nullable=False)
    
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=True)
    asset_config = Column(JSONB, nullable=True)

    asset_project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="assets")

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_assets_project_id', 'id'),
        Index('ix_asset_type', 'uuid'),
    )
    
    data_chunks = relationship("DataChunk", back_populates="asset")

