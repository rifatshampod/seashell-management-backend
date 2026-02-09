from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date, datetime


class SeashellCreate(BaseModel):
    name: str
    species: str
    description: Optional[str] = None
    color: Optional[str] = None
    size_mm: Optional[int] = None
    found_on: Optional[date] = None
    found_at: Optional[str] = None
    storage_location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None


class SeashellResponse(BaseModel):
    id: UUID
    name: str
    species: str
    description: Optional[str]
    color: Optional[str]
    size_mm: Optional[int]
    found_on: Optional[date]
    found_at: Optional[str]
    storage_location: Optional[str]
    condition: Optional[str]
    notes: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SeashellUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    size_mm: Optional[int] = None
    found_on: Optional[date] = None
    found_at: Optional[str] = None
    storage_location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
