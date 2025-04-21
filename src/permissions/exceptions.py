from fastapi import HTTPException, status

from ..core.AbsractHTTPExceptions import AbstractHTTPExceptions


class PermissionsHTTPExceptions(AbstractHTTPExceptions):
    
    def not_found_404(self, detail: str = "") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    
    def conflict_409(self, detail: str = "") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    
    
    def forbidden_403(self, detail: str = "You have no permissions on this course") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )