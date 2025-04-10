from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict



# Работа с непосредственно самими курсами
class CourseBaseSchema(BaseModel):
    """Схема для чтения и вывода информации о курсе."""

    id: UUID = Field(..., description="Уникальный идентификатор курса")
    channel_id: str = Field(..., description="Идентификатор канала, к которому привязан курс")
    name: str = Field(..., min_length=1, max_length=100, description="Название курса")
    student_count: int = Field(default=0, ge=0, description="Количество студентов, записанных на курс")
    preview: Optional[str] = Field(None, max_length=1000, description="Ссылка на превью курса")
    created_at: datetime = Field(..., description="Дата и время создания курса")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления курса")

    

class CourseCreateSchema(CourseBaseSchema): pass
class CourseUpdateSchema(CourseBaseSchema): pass
class CourseReadSchema(CourseBaseSchema): 
    model_config = ConfigDict(from_attributes=True)


# Работа со структурой курсов
class LessonHWBaseSchema(BaseModel):
    """Схема домашнего задания для урока."""

    description: Optional[str] = Field(None, description="Описание домашнего задания")
    files: Optional[List[str]] = Field(None, description="Файлы, прикрепленные к заданию")

class LessonHWCreateSchema(LessonHWBaseSchema): pass
class LessonHWUpdateSchema(LessonHWBaseSchema): pass
class LessonHWReadSchema(LessonHWBaseSchema): 
    model_config = ConfigDict(from_attributes=True)



class StructureLessonBaseSchema(BaseModel):
    """Схема отдельного урока в курсе."""

    name: str = Field(..., min_length=1, max_length=100, description="Название урока")
    homework: Optional[LessonHWReadSchema] = Field(None, description="Домашнее задание урока")
    content: Optional[List[str]] = Field(None, description="Контент урока (ссылки на видео, PDF и т.д.)")

class StructureLessonCreateSchema(StructureLessonBaseSchema): pass
class StructureLessonUpdateSchema(StructureLessonBaseSchema): pass
class StructureLessonReadSchema(StructureLessonBaseSchema): 
    model_config = ConfigDict(from_attributes=True)



class StructureSubModuleBaseSchema(BaseModel):
    """Схема подмодуля, содержащего список уроков."""

    name: str = Field(..., min_length=1, max_length=100, description="Название подмодуля")
    lessons: List[StructureLessonReadSchema] = Field(..., description="Список уроков в подмодуле")

class StructureSubModuleCreateSchema(StructureSubModuleBaseSchema): pass
class StructureSubModuleUpdateSchema(StructureSubModuleBaseSchema): pass
class StructureSubModuleReadSchema(StructureSubModuleBaseSchema): 
    model_config = ConfigDict(from_attributes=True)



class StructureModuleBaseSchema(BaseModel):
    """Схема модуля курса, который может включать подмодули и уроки."""

    name: str = Field(..., min_length=1, max_length=100, description="Название модуля")
    is_active: bool = Field(True, description="Активность модуля (доступность для студентов)")
    submodules: Optional[List["StructureSubModuleReadSchema"]] = Field(None, description="Подмодули данного модуля")
    lessons: Optional[List[StructureLessonReadSchema]] = Field(None, description="Уроки непосредственно в модуле")

class StructureModuleCreateSchema(StructureModuleBaseSchema): pass
class StructureModuleUpdateSchema(StructureModuleBaseSchema): pass
class StructureModuleReadSchema(StructureModuleBaseSchema): 
    model_config = ConfigDict(from_attributes=True)



class FullStructureBaseSchema(BaseModel):
    """Полная схема структуры курса, состоящая из модулей."""
    modules: List[StructureModuleReadSchema] = Field(..., description="Список модулей в курсе")

class FullStructureCreateSchema(FullStructureBaseSchema):pass
class FullStructureUpdateSchema(FullStructureBaseSchema):pass
class FullStructureReadSchema(FullStructureBaseSchema):
    model_config = ConfigDict(from_attributes=True)



class StructureBaseSchema(BaseModel):
    """Схема создания нового курса."""
    channel_id: str = Field(..., description="Идентификатор канала, к которому привязан курс")
    structure: FullStructureReadSchema = Field(..., description="Полная структура курса")

class StructureCreateSchema(StructureBaseSchema): pass
class StructureUpdateSchema(StructureBaseSchema): pass
class StructureReadSchema(StructureBaseSchema): 
    model_config = ConfigDict(from_attributes=True)