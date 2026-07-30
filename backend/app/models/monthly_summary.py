from sqlalchemy import Column, Integer, String, Numeric, UniqueConstraint
from ..database import Base

class MonthlySummary(Base):
    __tablename__ = "monthly_summaries"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    total_expenses = Column(Numeric(10, 2), default=0)
    total_votes = Column(Integer, default=0)
    total_meals_served = Column(Integer, default=0)
    average_rating = Column(Numeric(3, 2), default=0)
    details_json = Column(String(5000), nullable=True)
    __table_args__ = (UniqueConstraint("month", "year", name="uq_month_year"),)
