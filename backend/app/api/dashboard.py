from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..api import menu, votes, ratings, mess_duty, off_days
from ..schemas.menu import MealTypeResponse, MenuItemResponse
from ..schemas.vote import VoteResponse
from ..schemas.rating import RatingResponse
from ..schemas.off_day import OffDayResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thin aggregator over the existing per-resource queries.

    Runs every query the dashboard needs in a single DB session / auth check
    and returns them together, so the UI can load the page with one request
    instead of six. The individual endpoints remain the source of truth for
    other pages; this just reuses their query functions.
    """
    meal_types = menu.list_meal_types(db=db)
    menu_items = menu.get_menu_by_date(menu_date=target_date, db=db)
    my_votes = votes.get_my_votes(vote_date=target_date, db=db, current_user=current_user)
    my_ratings = ratings.get_my_ratings(rating_date=target_date, db=db, current_user=current_user)
    duty = mess_duty.get_current_duty_users(db=db)
    off_day_list = off_days.list_off_days(db=db, user=current_user)

    return {
        "date": str(target_date),
        "meal_types": [MealTypeResponse.model_validate(m) for m in meal_types],
        "menu_items": [MenuItemResponse.model_validate(m) for m in menu_items],
        "my_votes": [VoteResponse.model_validate(v) for v in my_votes],
        "my_ratings": [RatingResponse.model_validate(r) for r in my_ratings],
        "mess_duty": duty,
        "off_days": [OffDayResponse.model_validate(o) for o in off_day_list],
    }
