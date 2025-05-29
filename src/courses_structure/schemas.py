from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, model_validator


class StructureLessonBaseSchema(BaseModel):
    """Урок в курсе"""

    name: str = Field(..., min_length=1, max_length=100, description="Название урока")
    homework: bool = Field(default=False, description="Является ли страница урока домашним заданием")
    content: Optional[List[str]] = Field(None, description="Контент урока (ссылки на видео, md и т.д.)")

class StructureLessonCreateSchema(StructureLessonBaseSchema): pass
class StructureLessonUpdateSchema(StructureLessonBaseSchema): pass
class StructureLessonReadSchema(StructureLessonBaseSchema): 
    model_config = ConfigDict(from_attributes=True)


class StructureSubModuleBaseSchema(BaseModel):
    """Схема подмодуля, содержащего список уроков."""

    name: str = Field(..., min_length=1, max_length=100, description="Название подмодуля")
    lessons: Optional[List[StructureLessonReadSchema]] = Field(..., description="Список уроков в подмодуле")

class StructureSubModuleCreateSchema(StructureSubModuleBaseSchema): pass
class StructureSubModuleUpdateSchema(StructureSubModuleBaseSchema): pass
class StructureSubModuleReadSchema(StructureSubModuleBaseSchema): 
    model_config = ConfigDict(from_attributes=True)


class StructureModuleBaseSchema(BaseModel):
    """Схема модуля курса, который может включать подмодули и уроки."""

    name: str = Field(..., min_length=1, max_length=100, description="Название модуля")
    is_active: bool = Field(True, description="Активность модуля (доступность для студентов)")
    submodules: Optional[List["StructureSubModuleReadSchema"]] = Field(None, description="Подмодули модуля")

class StructureModuleCreateSchema(StructureModuleBaseSchema): pass
class StructureModuleUpdateSchema(StructureModuleBaseSchema): pass
class StructureModuleReadSchema(StructureModuleBaseSchema): 
    model_config = ConfigDict(from_attributes=True)


class StructureItemSchema(BaseModel):
    """Обёртка для элементов структуры курса: модуль, подмодуль или урок"""
    module: Optional[StructureModuleReadSchema] = None
    submodule: Optional[StructureSubModuleReadSchema] = None
    lesson: Optional[StructureLessonReadSchema] = None

    @model_validator(mode="before")
    @classmethod
    def check_only_one(cls, values):
        set_fields = [k for k in ["module", "submodule", "lesson"] if values.get(k) is not None]
        if len(set_fields) != 1:
            raise ValueError("Ровно одно из полей [module, submodule, lesson] должно быть задано")
        return values


class StructureBaseSchema(BaseModel):
    content: List[StructureItemSchema] = Field(
        ..., 
        description="Вариативная структура курса — список модулей, подмодулей или уроков"
    )


class StructureCreateSchema(StructureBaseSchema): pass
class StructureReadSchema(StructureBaseSchema): pass
class StructureUpdateSchema(StructureBaseSchema): pass


class FullStructureBaseSchema(BaseModel):
    """Полная схема структуры курса, состоящая из модулей."""
    structure : StructureBaseSchema

class FullStructureCreateSchema(FullStructureBaseSchema):pass
class FullStructureUpdateSchema(FullStructureBaseSchema):pass
class FullStructureReadSchema(FullStructureBaseSchema):
    model_config = ConfigDict(from_attributes=True)
