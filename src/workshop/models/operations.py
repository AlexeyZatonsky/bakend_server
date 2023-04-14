from datetime import date
from decimal import Decimal
from pydantic import BaseModel



class Operation(BaseModel):
    id: int
    description: str
