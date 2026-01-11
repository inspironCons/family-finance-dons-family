from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from ..database import get_db
from .. import models
from ..config import settings
from ..services.ai_advisor import get_financial_advice

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def reports_page(request: Request, db: Session = Depends(get_db)):
    # Filter bulan ini (sederhana)
    today = date.today()
    start_date = date(today.year, today.month, 1)
    
    # Ambil semua transaksi bulan ini
    transactions = db.query(models.Transaction).filter(
        models.Transaction.date >= start_date
    ).all()
    
    # Hitung Pemasukan vs Pengeluaran
    total_income = sum(t.amount for t in transactions if t.category.category_type == models.TransactionType.INCOME)
    total_expense = sum(t.amount for t in transactions if t.category.category_type == models.TransactionType.EXPENSE)
    net_cashflow = total_income - total_expense
    
    # Hitung Pengeluaran per Kategori untuk Chart
    category_stats = db.query(
        models.Category.name,
        models.Category.icon,
        models.Category.priority_group,
        func.sum(models.Transaction.amount).label("total")
    ).join(models.Transaction).filter(
        models.Transaction.date >= start_date,
        models.Category.category_type == models.TransactionType.EXPENSE
    ).group_by(models.Category.id).order_by(func.sum(models.Transaction.amount).desc()).all()
    
    # Siapkan data untuk Chart.js (List of Labels & Data)
    chart_labels = [stat.name for stat in category_stats]
    chart_data = [stat.total for stat in category_stats]
    chart_colors = []
    
    # Warna dinamis berdasarkan priority group dengan variasi opacity/shade
    base_colors = {
        models.PriorityGroup.FIXED: [
            '#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB' # Shades of Gray
        ],
        models.PriorityGroup.LIVING: [
            '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD' # Shades of Blue
        ],
        models.PriorityGroup.LIFESTYLE: [
            '#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD' # Shades of Purple
        ]
    }
    
    group_counters = {g: 0 for w, g in zip([0]*3, models.PriorityGroup)}
    
    for stat in category_stats:
        group = stat.priority_group
        colors = base_colors.get(group, ['#E5E7EB'])
        # Ambil warna secara bergantian dalam grupnya
        color_idx = group_counters[group] % len(colors)
        chart_colors.append(colors[color_idx])
        group_counters[group] += 1
            
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_cashflow": net_cashflow,
        "category_stats": category_stats,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "chart_colors": chart_colors,
        "month_name": today.strftime("%B %Y")
        # Hapus ai_insight dari sini karena akan dipindah ke halaman khusus
    })

@router.get("/advisor")
def advisor_page(request: Request):
    return templates.TemplateResponse("advisor.html", {"request": request})

@router.post("/analyze")
async def analyze_finances(db: Session = Depends(get_db)):
    # 1. Cek Cache Harian dulu
    today_advice = db.query(models.AIAdvice).filter(
        func.date(models.AIAdvice.created_at) == date.today()
    ).first()
    
    if today_advice:
        return {"status": "success", "message": today_advice.content, "source": "cache"}

    if not settings.GEMINI_API_KEY:
        return {"status": "error", "message": "API Key Gemini belum disetting."}

    # 2. Ambil Data
    today = date.today()
    start_date = date(today.year, today.month, 1)
    
    transactions = db.query(models.Transaction).filter(models.Transaction.date >= start_date).all()
    total_income = sum(t.amount for t in transactions if t.category.category_type == models.TransactionType.INCOME)
    total_expense = sum(t.amount for t in transactions if t.category.category_type == models.TransactionType.EXPENSE)
    
    # Top Cats
    top_cats_query = db.query(
        models.Category.name,
        func.sum(models.Transaction.amount).label("total")
    ).join(models.Transaction).filter(
        models.Transaction.date >= start_date,
        models.Category.category_type == models.TransactionType.EXPENSE
    ).group_by(models.Category.id).order_by(func.sum(models.Transaction.amount).desc()).limit(3).all()
    
    top_cats_simple = [{"name": c.name, "total": c.total} for c in top_cats_query]

    # 3. Panggil Gemini
    try:
        advice_text = get_financial_advice(total_income, total_expense, top_cats_simple)
        
        # Simpan Cache
        if "sedang pusing" not in advice_text:
            new_advice = models.AIAdvice(content=advice_text)
            db.add(new_advice)
            db.commit()
            
        return {"status": "success", "message": advice_text, "source": "api"}
        
    except Exception as e:
        return {"status": "error", "message": "Gagal menghubungi AI."}
