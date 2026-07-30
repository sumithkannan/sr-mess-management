from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class OffDay(Base):
    __tablename__ = "off_days"
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    reason = Column(String(200), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
