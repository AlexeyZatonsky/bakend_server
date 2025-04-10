from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from .models import AccessLevelEnum



class UsersPermissionsBase(BaseModel):
    user_id : UUID
    course_id : UUID
    access_level : AccessLevelEnum

class UsersPermissionsCreate(UsersPermissionsBase):
    pass

class UsersPermissionsRead(UsersPermissionsBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)