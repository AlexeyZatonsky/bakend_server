from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession



from .service import PermissionsService
from .schemas import UsersPermissionsRead
from .exceptions import UsersPermissionsHTTPExceptions