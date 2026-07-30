from pydantic import BaseModel
from datetime import date

class VoteCreate(BaseModel):
    menu_item_id: int
    meal_type_id: int
    vote_date: date

class VoteResponse(BaseModel):
    id: int
    user_id: int
    menu_item_id: int
    meal_type_id: int
    vote_date: date
    class Config:
        from_attributes = True
