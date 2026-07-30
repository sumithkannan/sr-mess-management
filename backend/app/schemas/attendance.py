from pydantic import BaseModel
from typing import List
from datetime import date as date_type

class AttendanceCreate(BaseModel):
    user_id: int
    meal_type_id: int
    date: date_type

class AttendanceBatchCreate(BaseModel):
    meal_type_id: int
    date: date_type
    user_ids: List[int]

class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    meal_type_id: int
    date: date_type
    marked_by: int
    class Config:
        from_attributes = True
