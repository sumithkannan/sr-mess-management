from pydantic import BaseModel
from typing import Optional
from datetime import date as date_type, time

class MealTypeCreate(BaseModel):
    name: str
    start_time: time
    end_time: time
    vote_cutoff_hours: int = 12
    vote_open_interval_days: int = 7
    rating_start_hours: int = 2
    attendance_buffer_hours: int = 1
    sort_order: int = 0

class MealTypeUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    vote_cutoff_hours: Optional[int] = None
    vote_open_interval_days: Optional[int] = None
    rating_start_hours: Optional[int] = None
    attendance_buffer_hours: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class MealTypeResponse(BaseModel):
    id: int
    name: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    vote_cutoff_hours: int = 12
    vote_open_interval_days: int = 7
    rating_start_hours: int = 2
    attendance_buffer_hours: int = 1
    sort_order: int
    is_active: bool
    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    meal_type_id: int
    item_name: str
    description: Optional[str] = None
    date: Optional[date_type] = None
    day_of_week: Optional[int] = None
    is_recurring: bool = False

class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    day_of_week: Optional[int] = None
    is_available: Optional[bool] = None

class MenuItemResponse(BaseModel):
    id: int
    meal_type_id: int
    item_name: str
    description: Optional[str] = None
    date: Optional[date_type] = None
    day_of_week: Optional[int] = None
    is_recurring: bool
    is_available: bool
    class Config:
        from_attributes = True
