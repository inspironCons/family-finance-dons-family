from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
import calendar
from .database import engine, Base, get_db
from . import models, crud, schemas
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from .routers import transactions, wallets, account, reports, auth
from .services.scheduler import start_scheduler
from .config import settings

# Create Tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Finance PWA")

# Middleware untuk Cek Login (Protect Routes)
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Daftar URL yang boleh diakses tanpa login
    public_routes = [
        "/auth/login", 
        "/static", 
        "/favicon.ico", 
        "/manifest.json", 
        "/docs", 
        "/openapi.json"
    ]
    
    # Cek apakah path saat ini ada di public_routes
    is_public = any(request.url.path.startswith(route) for route in public_routes)
    
    # Cek Session
    user = request.session.get("user")
    
    if not is_public and not user:
        # Jika bukan public route dan tidak ada user, redirect ke login
        return RedirectResponse(url="/auth/login", status_code=303)
    
    response = await call_next(request)
    return response

# Add Session Middleware (1 Hour Timeout)
# Registered AFTER auth_middleware so it executes BEFORE it (LIFO)
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY, 
    max_age=3600 # 1 Jam
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(transactions.router)
app.include_router(wallets.router)
app.include_router(account.router)
app.include_router(reports.router)
app.include_router(auth.router)

# Templates
templates = Jinja2Templates(directory="templates")

# Dependency untuk Seeding Data Awal
def seed_data(db: Session):
    # Cek apakah kategori sudah ada
    if not db.query(models.Category).first():
        print("🌱 Seeding initial data...")
        
        # 1. Kategori Pemasukan
        incomes = [
            {"name": "Gaji Bulanan", "category_type": "income", "icon": "money"},
            {"name": "Bonus/THR", "category_type": "income", "icon": "gift"},
        ]
        for inc in incomes:
            db.add(models.Category(**inc))
            
        # 2. Kategori Pengeluaran (3 Buckets)
        expenses = [
            # Fixed (Kewajiban)
            {"name": "KPR", "category_type": "expense", "priority_group": "fixed", "icon": "house"},
            {"name": "Listrik", "category_type": "expense", "priority_group": "fixed", "icon": "lightning"},
            
            # Living (Kebutuhan)
            {"name": "Belanja", "category_type": "expense", "priority_group": "living", "icon": "shopping-cart"},
            {"name": "Bensin/Transport", "category_type": "expense", "priority_group": "living", "icon": "gas-pump"},
            {"name": "Pulsa/Internet", "category_type": "expense", "priority_group": "living", "icon": "wifi-high"},
            
            # Lifestyle (Keinginan)
            {"name": "Jajan", "category_type": "expense", "priority_group": "lifestyle", "icon": "coffee"},
            {"name": "Makan Luar", "category_type": "expense", "priority_group": "lifestyle", "icon": "fork-knife"},
            {"name": "Langganan Digital", "category_type": "expense", "priority_group": "lifestyle", "icon": "film-strip"},
        ]
        for exp in expenses:
            db.add(models.Category(**exp))
            
        # 3. Wallet Default
        wallets = [
            {"name": "Dompet Tunai", "wallet_type": "Cash", "initial_balance": 0},
        ]
        for w in wallets:
            db.add(models.Wallet(**w))
            
        db.commit()
        print("✅ Seeding complete!")

@app.on_event("startup")
def on_startup():
    # Trigger seeding saat aplikasi nyala
    with Session(engine) as session:
        seed_data(session)

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    wallets = crud.get_wallets(db)
    recent_transactions = db.query(models.Transaction).order_by(models.Transaction.date.desc()).limit(5).all()
    
    total_balance = sum(w.initial_balance for w in wallets)
    
    # Hitung Statistik Bulan Ini
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    # Total Pengeluaran Bulan Ini
    month_expense = db.query(func.sum(models.Transaction.amount))\
        .join(models.Category)\
        .filter(
            models.Transaction.date >= start_of_month,
            models.Category.category_type == models.TransactionType.EXPENSE
        ).scalar() or 0.0
        
    # Total Pemasukan Bulan Ini (Asumsi sebagai budget)
    month_income = db.query(func.sum(models.Transaction.amount))\
        .join(models.Category)\
        .filter(
            models.Transaction.date >= start_of_month,
            models.Category.category_type == models.TransactionType.INCOME
        ).scalar() or 0.0
        
    remaining_budget = max(0, month_income - month_expense)
    
    # Hitung Jatah Harian
    last_day = calendar.monthrange(today.year, today.month)[1]
    days_remaining = (last_day - today.day) + 1
    daily_allowance = remaining_budget / days_remaining if days_remaining > 0 else remaining_budget
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "wallets": wallets,
        "transactions": recent_transactions,
        "total_balance": total_balance,
        "month_expense": month_expense,
        "remaining_budget": remaining_budget,
        "daily_allowance": daily_allowance
    })