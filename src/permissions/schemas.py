from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from .models import PermissionsEnum



class PermissionBaseSchema(BaseModel):
    user_id: UUID = Field(..., description="ID пользователя")
    course_id: UUID = Field(..., description="ID курса")


class PermissionCreateSchema(PermissionBaseSchema):
    access_level: PermissionsEnum = Field(
        PermissionsEnum.STUDENT,
        description="Уровень доступа (по умолчанию STUDENT)"
    )
    expiration_date: Optional[datetime] = Field(
        None,
        description="Дата окончания действия прав (None — бессрочно)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )


class PermissionUpdateSchema(BaseModel):
    access_level: Optional[PermissionsEnum] = Field(
        None,
        description="Новый уровень доступа (если нужно сменить)"
    )
    expiration_date: Optional[datetime] = Field(
        None,
        description="Новая дата окончания действия прав"
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )


class PermissionReadSchema(PermissionBaseSchema):
    access_level: PermissionsEnum = Field(..., description="Уровень доступа")
    granted_at: datetime = Field(..., description="Когда права были выданы")
    expiration_date: Optional[datetime] = Field(
        None,
        description="Когда права истекают (None — бессрочно)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )