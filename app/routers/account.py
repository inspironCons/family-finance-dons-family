from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, crud

router = APIRouter(prefix="/account", tags=["account"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def account_page(request: Request, db: Session = Depends(get_db)):
    # Ambil semua kategori
    categories = db.query(models.Category).all()
    
    # Kelompokkan kategori berdasarkan tipe dan priority group
    income_cats = [c for c in categories if c.category_type == models.TransactionType.INCOME]
    
    expense_fixed = [c for c in categories if c.priority_group == models.PriorityGroup.FIXED]
    expense_living = [c for c in categories if c.priority_group == models.PriorityGroup.LIVING]
    expense_lifestyle = [c for c in categories if c.priority_group == models.PriorityGroup.LIFESTYLE]
    
    return templates.TemplateResponse("account.html", {
        "request": request,
        "income_cats": income_cats,
        "expense_fixed": expense_fixed,
        "expense_living": expense_living,
        "expense_lifestyle": expense_lifestyle
    })

@router.post("/category/add")
def add_category(
    name: str = Form(...),
    type: str = Form(...), # income / expense
    group: str = Form(None), # fixed / living / lifestyle
    icon: str = Form("tag"),
    db: Session = Depends(get_db)
):
    new_cat = models.Category(
        name=name,
        category_type=type,
        priority_group=group if type == 'expense' else None,
        icon=icon
    )
    db.add(new_cat)
    db.commit()
    return RedirectResponse(url="/account", status_code=303)

@router.post("/reset_data")
def reset_data(db: Session = Depends(get_db)):
    # Hapus semua transaksi
    db.query(models.Transaction).delete()
    
    # Reset saldo dompet ke initial
    wallets = db.query(models.Wallet).all()
    for w in wallets:
        w.initial_balance = 0
        w.is_active = 1
        
    db.commit()
    return RedirectResponse(url="/", status_code=303)
