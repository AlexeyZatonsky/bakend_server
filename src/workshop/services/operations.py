from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import Operation
from ..database import get_session
from ..database import tables

'''class OperationService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, operation_id: int) -> tables.TableData:
        operation = (
            self.session
            .query(tables.TableData)
            .filter_by(id = operation_id)
            .first()
        )
        if not operation:
            raise HTTPException(status_code=404)
        return operation
    
    def get(self, operation_id: int)-> tables.TableData:
        return self._get(operation_id)'''