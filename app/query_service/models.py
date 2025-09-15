from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.db import Base


class Request(Base):
    __tablename__ = "requests"
    __table_args__ = (
        Index("ix_requests_cadastral_number_created_at", "cadastral_number", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    cadastral_number = Column(String(128), index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    payload = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

