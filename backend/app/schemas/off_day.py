from pydantic import BaseModel
from typing import Optional
from datetime import date

class OffDayCreate(BaseModel):
    start_date: date
    end_date: date
    reason: Optional[str] = None

class OffDayResponse(BaseModel):
    id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
