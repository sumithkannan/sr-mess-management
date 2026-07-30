from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from ..dependencies import get_db, admin_required
from ..models.expense import Expense
from ..schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])

@router.get("", response_model=list[ExpenseResponse])
def list_expenses(month: int = Query(None), year: int = Query(None),
                  db: Session = Depends(get_db), admin=Depends(admin_required)):
    q = db.query(Expense)
    if month and year:
        q = q.filter(
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year
        )
    return q.order_by(Expense.expense_date.desc()).all()

@router.post("", response_model=ExpenseResponse)
def create_expense(req: ExpenseCreate, db: Session = Depends(get_db),
                   admin=Depends(admin_required)):
    exp = Expense(**req.model_dump(), created_by=admin.id)
    db.add(exp); db.commit(); db.refresh(exp)
    return ExpenseResponse.model_validate(exp)

@router.put("/{exp_id}", response_model=ExpenseResponse)
def update_expense(exp_id: int, req: ExpenseUpdate, db: Session = Depends(get_db),
                   admin=Depends(admin_required)):
    exp = db.query(Expense).filter(Expense.id == exp_id).first()
    if not exp: raise HTTPException(status_code=404)
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(exp, k, v)
    db.commit(); db.refresh(exp)
    return ExpenseResponse.model_validate(exp)

@router.delete("/{exp_id}")
def delete_expense(exp_id: int, db: Session = Depends(get_db),
                   admin=Depends(admin_required)):
    exp = db.query(Expense).filter(Expense.id == exp_id).first()
    if not exp: raise HTTPException(status_code=404)
    db.delete(exp); db.commit()
    return {"message": "Expense deleted"}

@router.get("/monthly-summary")
def get_monthly_summary(month: int, year: int, db: Session = Depends(get_db),
                        admin=Depends(admin_required)):
    total = db.query(func.sum(Expense.amount)).filter(
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year
    ).scalar() or 0
    count = db.query(Expense).filter(
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year
    ).count()
    return {"month": month, "year": year, "total_expenses": float(total), "total_entries": count}
