from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    expense_date = Column(Date, nullable=False)
    bill_image = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
