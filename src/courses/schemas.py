from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict



# Работа с непосредственно самими курсами
class CourseBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название курса")
    is_public: bool = Field(default=True, description="Является ли курс общедоступным")
    preview: Optional[str] = Field(None, max_length=1000, description="Ссылка на превью курса")
    

class CourseCreateSchema(CourseBaseSchema): pass

class CourseUpdateSchema(CourseBaseSchema): pass
class CourseReadSchema(CourseBaseSchema):
    id: UUID = Field(..., description="Уникальный идентификатор курса")
    channel_id: str = Field(..., description="Идентификатор канала, к которому привязан курс")
    owner_id: UUID = Field(description="ID владельца курса")
    name: str = Field(..., min_length=1, max_length=100, description="Название курса")
    is_public: bool = Field(default=True, description="Является ли курс общедоступным")
    student_count: int = Field(default=0, ge=0, description="Количество студентов, записанных на курс")
    preview: Optional[str] = Field(None, max_length=1000, description="Ссылка на превью курса")
    created_at: datetime = Field(..., description="Дата и время создания курса")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления курса")

    model_config = ConfigDict(from_attributes=True)