import logging
from ..core.log import configure_logging


from datetime import datetime, UTC, timedelta
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from .models import PermissionsEnum


logger = logging.getLogger(__name__)
configure_logging()


def plus_month() -> datetime:
    time = datetime.now(UTC) + timedelta(days=30)
    valid_datetime_str = "2025-07-01T00:00:00Z"
    logger.debug(f"calcilate dtm: {time}\nvalid_example: {valid_datetime_str}")
    return time

class PermissionBaseSchema(BaseModel):
    user_id: UUID = Field(..., description="ID пользователя которому выдаются права на курс")
    #course_id: UUID = Field(..., description="ID курса")


class PermissionCreateSchema(PermissionBaseSchema):
    access_level: PermissionsEnum = Field(
        PermissionsEnum.STUDENT,
        description="Уровень доступа (по умолчанию STUDENT)"
    )
    expiration_date: Optional[datetime] = Field(
        default_factory= plus_month(),
        description="Дата окончания действия прав (по умолчанию +30 дней; None — бессрочно)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )

    @field_validator("expiration_date", mode="before")
    def empty_to_none(cls, v):
        logger.debug(f"попали в метод валидации ")
        # обнуляем '', 'null', 'None', None
        if v is None or str(v).strip().lower() in {"", "null", "none"}:
            return None
        return v


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
    course_id: UUID = Field(..., description="Курс к которому выданы права")
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