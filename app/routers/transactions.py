from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
import calendar
from ..database import get_db
from .. import models, crud

router = APIRouter(prefix="/transactions", tags=["transactions"])
templates = Jinja2Templates(directory="templates")

@router.get("/history")
def transaction_history(
    request: Request,
    start_date: str = None, 
    end_date: str = None, 
    filter_type: str = "this_month",
    db: Session = Depends(get_db)
):
    today = date.today()
    
    # Logic Penentuan Tanggal
    if filter_type == "mtd":
        # Month to Date: Tanggal 1 s/d Hari Ini
        start_date_obj = date(today.year, today.month, 1)
        end_date_obj = today
        
    elif filter_type == "custom" and start_date and end_date:
        # Custom Range
        try:
            start_date_obj = date.fromisoformat(start_date)
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            # Fallback ke This Month jika format error
            start_date_obj = date(today.year, today.month, 1)
            end_date_obj = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
            filter_type = "this_month"
            
    else:
        # Default: This Month (Full)
        filter_type = "this_month"
        start_date_obj = date(today.year, today.month, 1)
        end_date_obj = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    
    transactions = db.query(models.Transaction).filter(
        models.Transaction.date >= start_date_obj,
        models.Transaction.date <= end_date_obj
    ).order_by(models.Transaction.date.desc()).all()
    
    return templates.TemplateResponse("transaction_history.html", {
        "request": request,
        "transactions": transactions,
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "filter_type": filter_type
    })

@router.get("/add")
def add_transaction_form(request: Request, db: Session = Depends(get_db)):
    # Filter hanya wallet aktif
    wallets = db.query(models.Wallet).filter(models.Wallet.is_active == 1).all()
    categories = db.query(models.Category).all()
    return templates.TemplateResponse("add_transaction.html", {
        "request": request, 
        "wallets": wallets, 
        "categories": categories,
        "today": date.today().isoformat()
    })

@router.post("/add")
def create_transaction(
    date: date = Form(...),
    amount: float = Form(...),
    description: str = Form(None),
    wallet_id: int = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Buat objek transaksi baru
    new_transaction = models.Transaction(
        date=date,
        amount=amount,
        description=description,
        wallet_id=wallet_id,
        category_id=category_id
    )
    
    # Update saldo dompet (logika sederhana)
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    
    if category.category_type == models.TransactionType.EXPENSE:
        wallet.initial_balance -= amount
    else:
        wallet.initial_balance += amount
        
    db.add(new_transaction)
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@router.get("/transfer")
def transfer_form(request: Request, db: Session = Depends(get_db)):
    wallets = db.query(models.Wallet).filter(models.Wallet.is_active == 1).all()
    return templates.TemplateResponse("transfer.html", {
        "request": request,
        "wallets": wallets,
        "today": date.today().isoformat()
    })

@router.post("/transfer")
def process_transfer(
    date: date = Form(...),
    amount: float = Form(...),
    source_wallet_id: int = Form(...),
    target_wallet_id: int = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Ambil Dompet
    source = db.query(models.Wallet).filter(models.Wallet.id == source_wallet_id).first()
    target = db.query(models.Wallet).filter(models.Wallet.id == target_wallet_id).first()
    
    if not source or not target:
        raise HTTPException(status_code=404, detail="Wallet not found")
        
    # 2. Update Saldo
    source.initial_balance -= amount
    target.initial_balance += amount
    
    # 3. Cari atau Buat Kategori 'Transfer' (Agar tercatat di history)
    # Kita cari kategori sistem bernama 'Transfer'
    cat_transfer = db.query(models.Category).filter(models.Category.name == "Transfer").first()
    if not cat_transfer:
        # Jika belum ada, buat baru (Hidden category basically)
        cat_transfer = models.Category(name="Transfer", category_type=models.TransactionType.TRANSFER, icon="arrows-left-right")
        db.add(cat_transfer)
        db.commit()
        db.refresh(cat_transfer)

    # 4. Catat Transaksi
    # Kita catat sebagai pengeluaran dari Source? Atau 2 transaksi?
    # Cara paling rapi: 1 Record Transaksi tapi field wallet_id mengarah ke source.
    # Deskripsi otomatis ditambahkan info tujuan.
    
    tx_desc = f"Transfer ke {target.name}"
    if description:
        tx_desc += f" ({description})"

    new_tx = models.Transaction(
        date=date,
        amount=amount,
        description=tx_desc,
        wallet_id=source.id,
        category_id=cat_transfer.id
    )
    
    db.add(new_tx)
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)
