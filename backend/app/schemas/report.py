from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReportFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    meal_type_id: Optional[int] = None
    user_id: Optional[int] = None
