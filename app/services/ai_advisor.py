from google import genai
from google.genai import types
from ..config import settings
import logging
import os

logger = logging.getLogger(__name__)

def get_financial_advice(month_income, month_expense, top_categories):
    if not settings.GEMINI_API_KEY:
        return "API Key missing."

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        top_cat_str = ", ".join([f"{c['name']} (Rp {c['total']:,})" for c in top_categories])
        sisa_cashflow = month_income - month_expense
        
        # Baca Context dari File (Rahasia & Fleksibel)
        context_file_path = "context.txt" # Path di dalam container
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

        # Menggunakan Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(include_thoughts=False)
            )
        )
        print(f"DEBUG GEMINI RESPONSE: {response.text.strip()}")

        
        return response.text.strip()

    except Exception as e:
        import traceback
        print(f"DEBUG GEMINI ERROR FULL: {traceback.format_exc()}")
        logger.error(f"Gemini AI Error: {e}")
        return f"Waduh, AI-nya lagi bengong. Error: {str(e)}"
