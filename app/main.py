from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import calendar
from .database import engine, Base, get_db
from . import models, crud, schemas
from .routers import transactions, wallets, account, reports, auth
from .config import settings
# from .services.scheduler import start_scheduler # Disabled for MVP

# Create Tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Finance PWA")

# Middleware Auth Custom
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        allowed_paths = ["/auth/login", "/static", "/docs", "/openapi.json"]
        is_allowed = any(request.url.path.startswith(path) for path in allowed_paths)
        if not is_allowed and not request.session.get("user"):
            return RedirectResponse(url="/auth/login")
        response = await call_next(request)
        return response

app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=3600)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(wallets.router)
app.include_router(account.router)
app.include_router(reports.router)

templates = Jinja2Templates(directory="templates")

# Definisi seed_data HARUS di sini
def seed_data(db: Session):
    if not db.query(models.User).first():
        print("👤 Creating default user...")
        default_user = models.User(
            username="admin",
            full_name="Kepala Keluarga",
            pin_hash=settings.ADMIN_PIN
        )
        db.add(default_user)
        db.commit()

    if not db.query(models.Category).first():
        print("🌱 Seeding initial data...")
        incomes = [
            {"name": "Gaji Bulanan", "category_type": "income", "icon": "money"},
            {"name": "Bonus/THR", "category_type": "income", "icon": "gift"},
        ]
        for inc in incomes:
            db.add(models.Category(**inc))
            
        expenses = [
            {"name": "KPR", "category_type": "expense", "priority_group": "fixed", "icon": "house"},
            {"name": "Listrik", "category_type": "expense", "priority_group": "fixed", "icon": "lightning"},
            {"name": "Belanja", "category_type": "expense", "priority_group": "living", "icon": "shopping-cart"},
            {"name": "Bensin/Transport", "category_type": "expense", "priority_group": "living", "icon": "gas-pump"},
            {"name": "Pulsa/Internet", "category_type": "expense", "priority_group": "living", "icon": "wifi-high"},
            {"name": "Jajan", "category_type": "expense", "priority_group": "lifestyle", "icon": "coffee"},
            {"name": "Makan Luar", "category_type": "expense", "priority_group": "lifestyle", "icon": "fork-knife"},
            {"name": "Langganan Digital", "category_type": "expense", "priority_group": "lifestyle", "icon": "film-strip"},
        ]
        for exp in expenses:
            db.add(models.Category(**exp))
            
        wallets = [
            {"name": "Dompet Tunai", "wallet_type": "Cash", "initial_balance": 0},
        ]
        for w in wallets:
            db.add(models.Wallet(**w))
            
        db.commit()
        print("✅ Seeding complete!")

@app.on_event("startup")
def on_startup():
    with Session(engine) as session:
        seed_data(session)
    # start_scheduler() # Disabled

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    wallets = crud.get_wallets(db)
    transactions = db.query(models.Transaction).order_by(models.Transaction.date.desc()).limit(10).all()
    total_balance = sum(w.initial_balance for w in wallets)
    today = date.today()
    start_date = date(today.year, today.month, 1)
    tx_month = db.query(models.Transaction).filter(models.Transaction.date >= start_date, models.Transaction.date <= today).all()
    month_income = sum(t.amount for t in tx_month if t.category.category_type == models.TransactionType.INCOME)
    month_expense = sum(t.amount for t in tx_month if t.category.category_type == models.TransactionType.EXPENSE)
    remaining_budget = month_income - month_expense
    last_day = calendar.monthrange(today.year, today.month)[1]
    days_left = last_day - today.day + 1
    
    if days_left > 0 and remaining_budget > 0:
        daily_allowance = remaining_budget / days_left
    else:
        daily_allowance = 0
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "wallets": wallets,
        "transactions": transactions,
        "total_balance": total_balance,
        "daily_allowance": daily_allowance,
        "remaining_budget": remaining_budget,
        "month_expense": month_expense,
    })
