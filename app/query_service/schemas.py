"""Pydantic schemas for request input and output models."""

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class RequestCreate(BaseModel):
    """Incoming payload for creating a new request."""

    cadastral_number: str
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if v < -90 or v > 90:
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if v < -180 or v > 180:
            raise ValueError("longitude must be between -180 and 180")
        return v


class RequestRead(BaseModel):
    """Response schema representing a stored request."""

    id: int
    cadastral_number: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    payload: Optional[dict] = None
    response: Optional[dict] = None
    success: Optional[bool] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
