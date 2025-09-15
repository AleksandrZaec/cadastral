from pydantic import BaseModel, ConfigDict
from typing import Optional


class RequestCreate(BaseModel):
    cadastral_number: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RequestRead(BaseModel):
    id: int
    cadastral_number: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    payload: Optional[dict] = None
    response: Optional[dict] = None
    success: Optional[bool] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
