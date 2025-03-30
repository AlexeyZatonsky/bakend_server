from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CourseBaseSchema(BaseModel):
    """Базовая схема курса, содержащая основные атрибуты."""

    name: str = Field(..., min_length=1, max_length=255, description="Название курса")
    preview: Optional[str] = Field(None, max_length=1000, description="Ссылка на превью курса")


class LessonHWSchema(BaseModel):
    """Схема домашнего задания для урока."""

    description: Optional[str] = Field(None, description="Описание домашнего задания")
    files: Optional[List[str]] = Field(None, description="Файлы, прикрепленные к заданию")


class CourseLessonSchema(BaseModel):
    """Схема отдельного урока в курсе."""

    name: str = Field(..., min_length=1, max_length=100, description="Название урока")
    homework: Optional[LessonHWSchema] = Field(None, description="Домашнее задание урока")
    content: Optional[List[str]] = Field(None, description="Контент урока (ссылки на видео, PDF и т.д.)")


class CourseSubModuleSchema(BaseModel):
    """Схема подмодуля, содержащего список уроков."""

    name: str = Field(..., min_length=1, max_length=100, description="Название подмодуля")
    lessons: List[CourseLessonSchema] = Field(..., description="Список уроков в подмодуле")


class CourseModuleSchema(BaseModel):
    """Схема модуля курса, который может включать подмодули и уроки."""

    name: str = Field(..., min_length=1, max_length=100, description="Название модуля")
    is_active: bool = Field(True, description="Активность модуля (доступность для студентов)")
    submodules: Optional[List["CourseSubModuleSchema"]] = Field(None, description="Подмодули данного модуля")
    lessons: Optional[List[CourseLessonSchema]] = Field(None, description="Уроки непосредственно в модуле")


CourseModuleSchema.model_rebuild()


class FullCourseStructureSchema(BaseModel):
    """Полная схема структуры курса, состоящая из модулей."""

    modules: List[CourseModuleSchema] = Field(..., description="Список модулей в курсе")


class CourseCreateSchema(CourseBaseSchema):
    """Схема создания нового курса."""

    channel_id: str = Field(..., description="Идентификатор канала, к которому привязан курс")
    structure: FullCourseStructureSchema = Field(..., description="Полная структура курса")


class CourseReadSchema(CourseBaseSchema):
    """Схема для чтения и вывода информации о курсе."""

    id: UUID = Field(..., description="Уникальный идентификатор курса")
    channel_id: str = Field(..., description="Идентификатор канала, к которому привязан курс")
    student_count: int = Field(default=0, ge=0, description="Количество студентов, записанных на курс")
    created_at: datetime = Field(..., description="Дата и время создания курса")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления курса")
    structure: FullCourseStructureSchema = Field(..., description="Полная структура курса")

    model_config = ConfigDict(from_attributes=True)


class CourseUpdateSchema(BaseModel):
    """Схема обновления данных о курсе."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название курса")
    preview: Optional[str] = Field(None, max_length=1000, description="Ссылка на превью курса")
    structure: Optional[FullCourseStructureSchema] = Field(None, description="Обновлённая структура курса")

    model_config = ConfigDict(from_attributes=True)
