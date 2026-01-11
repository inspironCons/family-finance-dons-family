import google.generativeai as genai
from ..config import settings
import logging

logger = logging.getLogger(__name__)


USER_PROFILE = """
PROFIL KELUARGA:
- Kepala Keluarga: Karyawan (Gaji Tetap).
- Istri: Pengusaha (Income Fluktuatif).
- Anak: 1 orang (Balita, ~2 tahun).
- Utang: KPR (Sisa 515 Jt).
- Gaya Bahasa: Santai, suportif, "Bro/Sis", tapi tegas soal angka.

GOALS:
1. Short Term: Macbook Pro (Suami), Upgrade HRV RS (Istri), Umroh.
2. Long Term: Lunas KPR, Haji.
"""

def get_financial_advice(month_income, month_expense, top_categories):
    if not settings.GEMINI_API_KEY:
        return "API Key missing."

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Coba inisialisasi model (Gunakan 1.5 Flash jika 2.0 error/belum tersedia)
        # 1.5 Flash sangat cukup untuk task analisis teks seperti ini.
        model = genai.GenerativeModel('gemini-3-flash-preview') 

        # Format kategori
        top_cat_str = ", ".join([f"{c['name']} (Rp {c['total']})" for c in top_categories])
        sisa_cashflow = month_income - month_expense
        
        prompt = f"""
        {USER_PROFILE}

        LAPORAN BULAN INI:
        - Income: Rp {month_income}
        - Expense: Rp {month_expense}
        - Sisa Cashflow: Rp {sisa_cashflow}
        - Pengeluaran Terbesar: {top_cat_str}

        TUGAS (Jawab dalam Bahasa Indonesia yang natural):
        1. Diagnosis: Apakah cashflow bulan ini aman mengingat cicilan KPR & income istri yang fluktuatif?
        2. Action Plan: Alokasikan Rp {sisa_cashflow} ini kemana? (Pilih: Dana Darurat/Reksadana/Tabungan Goal). Prioritaskan Goal Macbook vs HRV mana yang lebih masuk akal dikejar duluan.
        3. Simulasi Kilat: Berapa bulan lagi salah satu goal tercapai jika konsisten seperti bulan ini?
        
        Keep it short, insightful, and actionable.
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        return "Waduh, AI-nya lagi bengong. Coba lagi nanti ya!"