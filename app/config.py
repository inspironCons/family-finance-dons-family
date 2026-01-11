import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Default ke 123456 jika tidak ada di env
    ADMIN_PIN = os.getenv("ADMIN_PIN", "123456") 
    SECRET_KEY = os.getenv("SECRET_KEY", "RAHASIA_SUPER_AMAN_JANGAN_DISEBAR")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Email Settings
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "noreply@financepwa.com")
    
    # AI Context (Privasi)
    # Default ini aman untuk publik. Prompt asli simpan di .env
    AI_PROMPT_CONTEXT = os.getenv("AI_PROMPT_CONTEXT", """
    PROFIL PENGGUNA:
    - Seorang manajer keuangan keluarga yang ingin berhemat.
    - Punya beberapa tujuan finansial jangka panjang.
    - Berikan saran yang umum namun memotivasi.
    """)

settings = Settings()
