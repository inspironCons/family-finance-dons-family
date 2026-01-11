from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models
from .email_service import send_report_email
from datetime import date
import logging

scheduler = AsyncIOScheduler()

async def job_send_report():
    """
    Fungsi ini akan dijalankan otomatis oleh scheduler.
    """
    db = SessionLocal()
    try:
        # Ambil pengaturan email dari DB (Misal user simpan di tabel User/Settings)
        # Untuk prototype, kita ambil email dari environment atau hardcoded user pertama
        user = db.query(models.User).first()
        if not user or not user.email: # Asumsi nanti kita tambah kolom email di tabel User
            logging.warning("No user email found for reporting.")
            return

        # Generate Laporan Singkat
        today = date.today()
        # ... logic hitung report (copy dari reports.py atau buat helper) ...
        # Untuk simpelnya, kita kirim teks dummy dulu
        report_html = "<h1>Laporan Keuangan Mingguan</h1><p>Halo, ini laporan otomatis Anda.</p>"
        
        await send_report_email(user.email, f"Laporan Keuangan {today}", report_html)
        
    except Exception as e:
        logging.error(f"Scheduler Error: {e}")
    finally:
        db.close()

def start_scheduler():
    # Contoh: Jalankan setiap hari jam 08:00 pagi
    # scheduler.add_job(job_send_report, 'cron', hour=8, minute=0)
    
    # Untuk Demo: Jalankan setiap 1 jam (interval)
    scheduler.add_job(job_send_report, 'interval', minutes=60)
    
    scheduler.start()
