from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
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


def _save_bill_image(data: bytes) -> str:
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
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

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(compressed)

        return f"/uploads/expenses/{filename}"
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")


def _remove_bill_file(bill_path: str):
    if not bill_path:
        return
    filename = os.path.basename(bill_path)
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
    except Exception:
        pass

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
    bill_path = _save_bill_image(data)
    
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


@router.put("/{exp_id}/upload", response_model=ExpenseResponse)
async def update_expense_with_upload(
    exp_id: int,
    description: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date: date = Form(...),
    bill: UploadFile = File(None),
    remove_bill: bool = Form(False),
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    exp = db.query(Expense).filter(Expense.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    exp.description = description
    exp.amount = Decimal(str(amount))
    exp.category = category
    exp.expense_date = expense_date

    if bill is not None:
        data = await bill.read()
        if data:
            new_path = _save_bill_image(data)
            _remove_bill_file(exp.bill_image)
            exp.bill_image = new_path
        elif remove_bill:
            _remove_bill_file(exp.bill_image)
            exp.bill_image = None
    elif remove_bill:
        _remove_bill_file(exp.bill_image)
        exp.bill_image = None

    db.commit(); db.refresh(exp)
    return ExpenseResponse.model_validate(exp)


@router.get("/{exp_id}/bill")
def get_expense_bill(exp_id: int, db: Session = Depends(get_db),
                     admin=Depends(admin_required)):
    exp = db.query(Expense).filter(Expense.id == exp_id).first()
    if not exp or not exp.bill_image:
        raise HTTPException(status_code=404, detail="Bill image not found")
    filepath = os.path.join(UPLOAD_DIR, os.path.basename(exp.bill_image))
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Bill image not found")
    return FileResponse(filepath, media_type="image/jpeg")


@router.delete("/{exp_id}")
def delete_expense(exp_id: int, db: Session = Depends(get_db),
                   admin=Depends(admin_required)):
    exp = db.query(Expense).filter(Expense.id == exp_id).first()
    if not exp: raise HTTPException(status_code=404)
    _remove_bill_file(exp.bill_image)
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
