from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    meal_type_id = Column(Integer, ForeignKey("meal_types.id"), nullable=False)
    date = Column(Date, nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "meal_type_id", "date", "menu_item_id", name="uq_rating"),
    )
