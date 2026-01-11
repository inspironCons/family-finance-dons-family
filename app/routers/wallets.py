from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from .. import models

router = APIRouter(prefix="/wallets", tags=["wallets"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_wallets(request: Request, db: Session = Depends(get_db)):
    wallets = db.query(models.Wallet).filter(models.Wallet.is_active == 1).all()
    
    # Hitung total aset
    total_balance = sum(w.initial_balance for w in wallets)
    
    return templates.TemplateResponse("wallets.html", {
        "request": request,
        "wallets": wallets,
        "total_balance": total_balance
    })

@router.get("/add")
def add_wallet_form(request: Request):
    return templates.TemplateResponse("add_wallet.html", {"request": request})

@router.post("/add")
def create_wallet(
    name: str = Form(...),
    wallet_type: str = Form(...),
    initial_balance: float = Form(0),
    db: Session = Depends(get_db)
):
    # Cek apakah nama dompet sudah ada (opsional)
    # ...
    
    new_wallet = models.Wallet(
        name=name,
        wallet_type=wallet_type,
        initial_balance=initial_balance,
        is_active=1
    )
    db.add(new_wallet)
    db.commit()
    
    return RedirectResponse(url="/wallets", status_code=303)

@router.get("/{wallet_id}/delete")
def delete_wallet_confirm(wallet_id: int, request: Request, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    other_wallets = db.query(models.Wallet).filter(models.Wallet.is_active == 1, models.Wallet.id != wallet_id).all()
    
    return templates.TemplateResponse("delete_wallet.html", {
        "request": request,
        "wallet": wallet,
        "other_wallets": other_wallets
    })

@router.post("/{wallet_id}/delete")
def delete_wallet(
    wallet_id: int, 
    action: str = Form(...), 
    target_wallet_id: int = Form(None),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    
    if not wallet:
        return RedirectResponse(url="/wallets", status_code=303)
        
    # Logika Transfer Saldo
    if wallet.initial_balance > 0 and action == "transfer" and target_wallet_id:
        target_wallet = db.query(models.Wallet).filter(models.Wallet.id == target_wallet_id).first()
        if target_wallet:
            amount = wallet.initial_balance
            
            # 1. Tambah saldo ke target
            target_wallet.initial_balance += amount
            
            # 2. Catat sebagai Transaksi Transfer (Opsional, tapi bagus untuk tracking)
            # Kita perlu kategori 'Transfer' atau sejenisnya. Untuk simpelnya kita skip pencatatan transaksi 
            # detil di tabel transaction agar tidak ribet dengan kategori ID, 
            # tapi secara logika uangnya pindah.
            
            # 3. Kosongkan saldo dompet lama
            wallet.initial_balance = 0
            
    # Soft Delete (Set Active = 0)
    wallet.is_active = 0
    db.commit()
        
    return RedirectResponse(url="/wallets", status_code=303)

@router.get("/{wallet_id}/adjust")
def adjust_balance_form(wallet_id: int, request: Request, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    return templates.TemplateResponse("adjust_wallet.html", {
        "request": request,
        "wallet": wallet,
        "today": date.today().isoformat()
    })

@router.post("/{wallet_id}/adjust")
def process_adjustment(
    wallet_id: int, 
    actual_balance: float = Form(...),
    description: str = Form(None),
    date_trx: date = Form(...),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        return RedirectResponse(url="/wallets", status_code=303)
        
    diff = actual_balance - wallet.initial_balance
    
    if diff == 0:
        return RedirectResponse(url="/wallets", status_code=303)

    # Cari/Buat Kategori Koreksi
    cat_adj = db.query(models.Category).filter(models.Category.name == "Koreksi Saldo").first()
    if not cat_adj:
        # Default sebagai Expense, tapi nanti fleksibel
        cat_adj = models.Category(
            name="Koreksi Saldo", 
            category_type=models.TransactionType.EXPENSE, 
            priority_group=models.PriorityGroup.LIFESTYLE,
            icon="scales"
        )
        db.add(cat_adj)
        db.commit()
        db.refresh(cat_adj)

    # Tentukan Tipe Transaksi (Income/Expense) berdasarkan selisih
    # Jika diff negatif (uang hilang) -> Expense
    # Jika diff positif (uang nemu) -> Income (Kita perlu akali kategori ini agar tidak error validasi jika ada constraint, 
    # tapi untuk simplifikasi kita pakai kategori Koreksi tadi, asumsi sistem fleksibel)
    
    # Update saldo dompet
    wallet.initial_balance = actual_balance
    
    # Catat Transaksi
    # Karena model Transaction tidak menyimpan 'type' (bergantung kategori), 
    # kita simpan ABS(amount).
    # NAMUN, kategori 'Koreksi Saldo' tadi kita set EXPENSE. 
    # Jika ini INCOME (Nemu uang), idealnya pakai kategori tipe INCOME.
    
    final_cat = cat_adj
    if diff > 0:
         # Uang Nemu -> Perlu kategori Income?
         # Mari kita buat kategori income koreksi jika belum ada
         cat_adj_inc = db.query(models.Category).filter(models.Category.name == "Koreksi Saldo (Income)").first()
         if not cat_adj_inc:
             cat_adj_inc = models.Category(name="Koreksi Saldo (Income)", category_type=models.TransactionType.INCOME, icon="scales")
             db.add(cat_adj_inc)
             db.commit()
         final_cat = cat_adj_inc

    new_tx = models.Transaction(
        date=date_trx,
        amount=abs(diff),
        description=f"Opname: {description or 'Selisih Saldo'}",
        wallet_id=wallet.id,
        category_id=final_cat.id
    )
    
    db.add(new_tx)
    db.commit()
    
    return RedirectResponse(url="/wallets", status_code=303)
