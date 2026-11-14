from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..api import menu
from ..schemas.menu import MealTypeResponse, MenuItemResponse

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("/dashboard")
def get_menu_dashboard(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thin aggregator over the menu page's queries (one session, one auth check)."""
    meal_types = menu.list_meal_types(db=db)
    date_items = menu.get_menu_by_date(menu_date=target_date, db=db)
    recurring_items = menu.get_recurring_menu(db=db)

    return {
        "date": str(target_date),
        "meal_types": [MealTypeResponse.model_validate(m) for m in meal_types],
        "date_items": [MenuItemResponse.model_validate(m) for m in date_items],
        "recurring_items": [MenuItemResponse.model_validate(m) for m in recurring_items],
    }
