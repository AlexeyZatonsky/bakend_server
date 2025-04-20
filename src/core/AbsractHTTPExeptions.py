from abc import ABC, abstractmethod
from fastapi import HTTPException, status


class AbstractHTTPExeptions(ABC):
    @abstractmethod
    def not_found_404(self, detail: str) -> HTTPException: ...
    
    @abstractmethod
    def conflict_409(self, detail: str) -> HTTPException: ...
    
    @abstractmethod
    def forbidden_403(self, detail: str) -> HTTPException: ...
