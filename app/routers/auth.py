from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, pin: str = Form(...), db: Session = Depends(get_db)):
    # Ambil user pertama (Single User App)
    user = db.query(models.User).first()
    
    # Jika user belum di-seed (seharusnya tidak terjadi), fallback ke default
    stored_pin = user.pin_hash if user else "512323"
    
    if pin == stored_pin:
        # Set Session
        request.session["user"] = user.username if user else "admin"
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "PIN Salah! Coba lagi."
        })

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
