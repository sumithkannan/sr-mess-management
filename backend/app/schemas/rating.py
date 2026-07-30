from pydantic import BaseModel
from typing import Optional
from datetime import date as date_type

class RatingCreate(BaseModel):
    menu_item_id: int
    meal_type_id: int
    date: date_type
    rating: int
    review: Optional[str] = None

class RatingResponse(BaseModel):
    id: int
    user_id: int
    menu_item_id: int
    meal_type_id: int
    date: date_type
    rating: int
    review: Optional[str] = None
    class Config:
        from_attributes = True
