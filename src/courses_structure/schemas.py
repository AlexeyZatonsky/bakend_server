from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict






class StructureLessonBaseSchema(BaseModel):
    """Урок в курсе - подразумевате в себе страницу в которой содержится контент в формате MD + что-то ещё (видео, фото)"""

    name: str = Field(..., min_length=1, max_length=100, description="Название урока")
    homework: bool = Field(default=False, description="Является ли страница урока домашним заданием (меняет только отображдение на фронте)")
    content: Optional[List[str]] = Field(None, description="Контент урока (ссылки на видео, PDF и т.д.)")

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
    submodules: Optional[List["StructureSubModuleReadSchema"]] = Field(None, description="Подмодули данного модуля !Сам модуль не может содержать в себе уроки - только подмодули")

class StructureModuleCreateSchema(StructureModuleBaseSchema): pass
class StructureModuleUpdateSchema(StructureModuleBaseSchema): pass
class StructureModuleReadSchema(StructureModuleBaseSchema): 
    model_config = ConfigDict(from_attributes=True)



class FullStructureBaseSchema(BaseModel):
    """Полная схема структуры курса, состоящая из модулей."""
    modules: (
        List[StructureModuleReadSchema] | 
        List[StructureSubModuleReadSchema] | 
        List[StructureLessonReadSchema]
    ) = Field(..., description="Структура содержания курса - List[Модуль] -> List[Пододуль] -> List[Урок] | List[Подмодль] -> List[Урок] | List[Урок]")

class FullStructureCreateSchema(FullStructureBaseSchema):pass
class FullStructureUpdateSchema(FullStructureBaseSchema):pass
class FullStructureReadSchema(FullStructureBaseSchema):
    model_config = ConfigDict(from_attributes=True)
