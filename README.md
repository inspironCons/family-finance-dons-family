# 🏠 Family Finance Tracker (PWA + AI Advisor)

Aplikasi manajemen keuangan keluarga berbasis web (Progressive Web App) yang dirancang untuk pelacakan transaksi yang ketat, cerdas, dan berorientasi pada tujuan masa depan. Dilengkapi dengan asisten finansial cerdas berbasis **Google Gemini AI**.

## ✨ Fitur Utama

- **🚀 Dashboard Finansial:** Pantau total saldo, indikator "runway" pengeluaran bulan ini, dan **Smart Daily Allowance** (jatah jajan harian otomatis).
- **🤖 Gemini AI Advisor:** Halaman khusus konsultasi keuangan. AI menganalisa data transaksi Anda dan memberikan strategi investasi konkret untuk mencapai impian (berdasarkan file konteks pribadi).
- **💸 Manajemen Transaksi:** Catat pemasukan dan pengeluaran dengan sistem **3 Bucket** (Fixed Cost, Living Cost, Lifestyle).
- **🏦 Multi-Wallet & Transfer:** Kelola banyak dompet (Cash, Bank, E-Wallet) dan lakukan transfer antar dompet (seperti tarik tunai ATM).
- **⚖️ Cash Opname:** Fitur penyesuaian saldo jika uang fisik tidak sesuai dengan aplikasi (otomatis mencatat selisih).
- **🔒 Secure Session:** Akses aplikasi aman dengan **PIN Keluarga** dan sistem *auto-logout* setiap 1 jam.
- **📱 PWA Ready:** Bisa di-install di HP (Android/iOS) dan terasa seperti aplikasi native.

## 🛡️ Keamanan & Privasi

Aplikasi ini dirancang untuk menjaga privasi data Anda:
- **Kontek Pribadi:** Semua profil keluarga dan tujuan finansial disimpan di file lokal `context.txt` (tidak di-push ke Git).
- **Secrets:** API Key dan PIN dikelola via Environment Variables.

## 🚀 Cara Menjalankan (Docker)

1.  **Clone Repositori:**
    ```bash
    git clone https://github.com/inspironCons/family-finance-dons-family.git
    cd family-finance-dons-family
    ```

2.  **Siapkan Konteks AI:**
    Buat file bernama `context.txt` di root folder dan isi dengan profil keluarga Anda. Contoh:
    ```text
    PROFIL KELUARGA:
    - Kepala Keluarga: Karyawan.
    - Istri: Pengusaha.
    ...
    ```

3.  **Jalankan dengan Docker CLI:**
    ```powershell
    docker build -t finance-pwa .
    docker run -d `
      -p 8000:8000 `
      -v ${PWD}/data:/app/data `
      -v ${PWD}/context.txt:/app/context.txt `
      -e ADMIN_PIN=512323 `
      -e GEMINI_API_KEY="KUNCI_API_ANDA" `
      --name family-finance-app `
      finance-pwa
    ```

4.  **Akses Aplikasi:**
    Buka `http://localhost:8000` (PIN Default: 512323 atau sesuai env).

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI
- **Database:** SQLite + SQLAlchemy
- **AI:** Google Gemini 1.5 Flash
- **Frontend:** Jinja2, Tailwind CSS, Chart.js, Marked.js (Markdown)

---
Dibuat dengan ❤️ untuk kemajuan finansial keluarga.