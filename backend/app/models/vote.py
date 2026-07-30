from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    meal_type_id = Column(Integer, ForeignKey("meal_types.id"), nullable=False)
    vote_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "meal_type_id", "vote_date", name="uq_vote"),
    )
