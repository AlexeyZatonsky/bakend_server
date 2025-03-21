from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    preview: Optional[str] = Field(None, max_length=1000)


class CourseCreate(CourseBase):
    channel_id: str
    structure: Dict[str, Any]


class CourseRead(CourseBase):
    id: UUID
    channel_id: str
    student_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseStructureBase(BaseModel):
    structure: Dict[str, Any]


class CourseStructureCreate(CourseStructureBase):
    course_id: UUID


class CourseStructureRead(CourseStructureBase):
    course_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    preview: Optional[str] = Field(None, max_length=1000)
    structure: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
