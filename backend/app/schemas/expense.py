from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class ExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    category: str
    expense_date: date

class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    expense_date: Optional[date] = None

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: Decimal
    category: str
    expense_date: date
    bill_image: Optional[str] = None
    created_by: int
    class Config:
        from_attributes = True
