from sqlalchemy import Column, Integer, String, Boolean, Time, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class MealType(Base):
    __tablename__ = "meal_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    vote_cutoff_hours = Column(Integer, default=12)
    vote_open_interval_days = Column(Integer, default=7)
    rating_start_hours = Column(Integer, default=2)
    attendance_buffer_hours = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint('meal_type_id', 'date', name='uix_meal_type_date'),
        UniqueConstraint('meal_type_id', 'day_of_week', name='uix_meal_type_dow'),
    )
    id = Column(Integer, primary_key=True, index=True)
    meal_type_id = Column(Integer, ForeignKey("meal_types.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    date = Column(Date, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    is_recurring = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
