from fastapi import HTTPException, status

from ..core.AbsractHTTPExeptions import AbstractHTTPExeptions


class ChannelsHTTPExeptions(AbstractHTTPExeptions):
    
    def not_found_404(self, detail: str = "Channels not found") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    
    def conflict_409(self, detail: str = "There is a channel with that name") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    
    
    def forbidden_403(self, detail: str = "You are not the owner of this channel") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )