import google.generativeai as genai
from ..config import settings
import logging
import os

logger = logging.getLogger(__name__)

def get_financial_advice(month_income, month_expense, top_categories):
    if not settings.GEMINI_API_KEY:
        return "API Key missing."

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-3-flash-preview')

        top_cat_str = ", ".join([f"{c['name']} (Rp {c['total']:,})" for c in top_categories])
        sisa_cashflow = month_income - month_expense
        
        # Baca Context dari File (Rahasia & Fleksibel)
        context_file_path = "context.txt" # Path di dalam container (root workdir /app)
        user_context = "User adalah keluarga yang ingin berhemat." # Default aman
        
        if os.path.exists(context_file_path):
            with open(context_file_path, "r", encoding="utf-8") as f:
                user_context = f.read()
        
        prompt = f"""
        {user_context}

        LAPORAN BULAN INI:
        - Income: Rp {month_income:,}
        - Expense: Rp {month_expense:,}
        - Sisa Cashflow: Rp {sisa_cashflow:,}
        - Pengeluaran Terbesar: {top_cat_str}

        TUGAS (Jawab dalam Bahasa Indonesia yang natural):
        1. Diagnosis: Apakah cashflow bulan ini aman?
        2. Action Plan: Alokasikan Rp {sisa_cashflow:,} ini kemana?
        3. Simulasi Kilat: Kapan goal tercapai?
        
        Keep it short, insightful, and actionable.
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        return "Waduh, AI-nya lagi bengong. Coba lagi nanti ya!"
