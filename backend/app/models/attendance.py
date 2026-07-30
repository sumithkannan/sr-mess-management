from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_type_id = Column(Integer, ForeignKey("meal_types.id"), nullable=False)
    date = Column(Date, nullable=False)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "meal_type_id", "date", name="uq_attendance"),
    )
