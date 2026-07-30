from pydantic import BaseModel
from typing import Optional
from datetime import date

class MessDutyCreate(BaseModel):
    user_id: int
    start_date: date
    end_date: date

class MessDutyUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class MessDutyResponse(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    created_by: int
    class Config:
        from_attributes = True
