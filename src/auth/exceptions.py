from fastapi import HTTPException, status

from ..core.AbsractHTTPExceptions import AbstractHTTPExceptions


class AuthHTTPExceptions(AbstractHTTPExceptions):
    
    def not_found_404(self, detail: str = "User not found") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    
    def conflict_409(self, detail: str = "User with this email already exists") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    
    
    def forbidden_403(self, detail: str = "This course does not belong to this channel") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
    
    def unauthorized_401(self, detail: str = "Not authenticated") -> HTTPException:
        """default - hasn't token"""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )