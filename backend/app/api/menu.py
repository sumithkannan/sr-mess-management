from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from ..dependencies import get_db, admin_required
from ..models.menu import MealType, MenuItem
from ..schemas.menu import (
    MealTypeCreate, MealTypeUpdate, MealTypeResponse,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse
)

router = APIRouter(prefix="/api", tags=["Menu"])

@router.get("/meal-types", response_model=list[MealTypeResponse])
def list_meal_types(db: Session = Depends(get_db)):
    return db.query(MealType).order_by(MealType.sort_order).all()

@router.post("/meal-types", response_model=MealTypeResponse)
def create_meal_type(req: MealTypeCreate, db: Session = Depends(get_db), admin=Depends(admin_required)):
    mt = MealType(**req.model_dump())
    db.add(mt); db.commit(); db.refresh(mt)
    return MealTypeResponse.model_validate(mt)

@router.put("/meal-types/{mt_id}", response_model=MealTypeResponse)
def update_meal_type(mt_id: int, req: MealTypeUpdate, db: Session = Depends(get_db), admin=Depends(admin_required)):
    mt = db.query(MealType).filter(MealType.id == mt_id).first()
    if not mt: raise HTTPException(status_code=404)
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(mt, k, v)
    db.commit(); db.refresh(mt)
    return MealTypeResponse.model_validate(mt)

@router.delete("/meal-types/{mt_id}")
def delete_meal_type(mt_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    mt = db.query(MealType).filter(MealType.id == mt_id).first()
    if not mt: raise HTTPException(status_code=404)
    db.delete(mt); db.commit()
    return {"message": "Meal type deleted"}

@router.get("/menu-items/date/{menu_date}", response_model=list[MenuItemResponse])
def get_menu_by_date(menu_date: date, db: Session = Depends(get_db)):
    dow = menu_date.weekday()
    date_items = db.query(MenuItem).filter(
        MenuItem.date == menu_date,
        MenuItem.is_available == True
    ).all()
    date_meal_type_ids = {i.meal_type_id for i in date_items}
    recurring_query = db.query(MenuItem).filter(
        MenuItem.is_recurring == True,
        MenuItem.day_of_week == dow,
        MenuItem.is_available == True
    )
    if date_meal_type_ids:
        recurring_query = recurring_query.filter(~MenuItem.meal_type_id.in_(date_meal_type_ids))
    recurring = recurring_query.all()
    return [MenuItemResponse.model_validate(i) for i in date_items + recurring]

@router.get("/menu-items/recurring", response_model=list[MenuItemResponse])
def get_recurring_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItem).filter(MenuItem.is_recurring == True).all()
    return [MenuItemResponse.model_validate(i) for i in items]

@router.post("/menu-items", response_model=MenuItemResponse)
def create_menu_item(req: MenuItemCreate, db: Session = Depends(get_db), admin=Depends(admin_required)):
    existing = None
    if req.is_recurring and req.day_of_week is not None:
        existing = db.query(MenuItem).filter(
            MenuItem.meal_type_id == req.meal_type_id,
            MenuItem.day_of_week == req.day_of_week,
            MenuItem.is_recurring == True
        ).first()
    elif req.date is not None:
        existing = db.query(MenuItem).filter(
            MenuItem.meal_type_id == req.meal_type_id,
            MenuItem.date == req.date
        ).first()
    if existing:
        existing.item_name = req.item_name
        existing.description = req.description
        db.commit(); db.refresh(existing)
        return MenuItemResponse.model_validate(existing)
    item = MenuItem(**req.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return MenuItemResponse.model_validate(item)

@router.put("/menu-items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: int, req: MenuItemUpdate, db: Session = Depends(get_db), admin=Depends(admin_required)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item: raise HTTPException(status_code=404)
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit(); db.refresh(item)
    return MenuItemResponse.model_validate(item)

@router.delete("/menu-items/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item: raise HTTPException(status_code=404)
    db.delete(item); db.commit()
    return {"message": "Menu item deleted"}

@router.post("/menu-items/generate/{menu_date}")
def generate_menu_from_recurring(menu_date: date, db: Session = Depends(get_db), admin=Depends(admin_required)):
    dow = menu_date.weekday()
    existing = db.query(MenuItem).filter(MenuItem.date == menu_date).count()
    if existing > 0:
        return {"message": f"Menu already has {existing} items for {menu_date}"}
    recurring = db.query(MenuItem).filter(
        MenuItem.is_recurring == True,
        MenuItem.day_of_week == dow
    ).all()
    count = 0
    for item in recurring:
        new_item = MenuItem(
            meal_type_id=item.meal_type_id,
            item_name=item.item_name,
            description=item.description,
            date=menu_date,
            is_recurring=False
        )
        db.add(new_item); count += 1
    db.commit()
    return {"message": f"Generated {count} menu items for {menu_date}"}
