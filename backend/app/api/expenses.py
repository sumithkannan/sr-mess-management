from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from datetime import date
from decimal import Decimal
from PIL import Image
import io, os, uuid
from ..dependencies import get_db, admin_required
from ..models.expense import Expense
from ..schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])

UPLOAD_DIR = "uploads/expenses"

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

@router.post("/upload", response_model=ExpenseResponse)
async def create_expense_with_upload(
    description: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date: date = Form(...),
    bill: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    data = await bill.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large")
    
    try:
        img = Image.open(io.BytesIO(data))
        img = img.convert('RGB')
        
        max_size = 1024
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        
        quality = 85
        for q in [85, 75, 65, 55]:
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=q, optimize=True)
            if buf.tell() <= 2 * 1024 * 1024:
                quality = q
                break
            quality = q
        
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        buf.seek(0)
        compressed = buf.read()
        
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(compressed)
        
        bill_path = f"/uploads/expenses/{filename}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    exp = Expense(
        description=description,
        amount=Decimal(str(amount)),
        category=category,
        expense_date=expense_date,
        bill_image=bill_path,
        created_by=admin.id
    )
    db.add(exp); db.commit(); db.refresh(exp)
    return ExpenseResponse.model_validate(exp)


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
