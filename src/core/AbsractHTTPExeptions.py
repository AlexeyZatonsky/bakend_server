from abc import ABC, abstractmethod
from fastapi import HTTPException, status


class AbstractHTTPErrors(ABC):
    @abstractmethod
    def not_found(self) -> HTTPException: ...
    
    @abstractmethod
    def conflict(self) -> HTTPException: ...
    
    @abstractmethod
    def forbidden(self) -> HTTPException: ...
