# 🏠 Family Finance Tracker (PWA + AI Advisor)

Aplikasi manajemen keuangan keluarga berbasis web (Progressive Web App) yang dirancang untuk pelacakan transaksi yang ketat, cerdas, dan berorientasi pada tujuan masa depan. Dilengkapi dengan asisten finansial cerdas berbasis **Google Gemini AI**.

## ✨ Fitur Utama

- **🚀 Dashboard Finansial:** Pantau total saldo, indikator "runway" pengeluaran bulan ini, dan **Smart Daily Allowance** (jatah jajan harian otomatis).
- **🤖 Gemini AI Advisor:** Halaman khusus konsultasi keuangan. AI menganalisa data transaksi Anda dan memberikan strategi investasi konkret untuk mencapai impian (Umroh, Haji, HRV RS, Macbook Pro, & Lunas KPR).
- **💸 Manajemen Transaksi:** Catat pemasukan dan pengeluaran dengan sistem **3 Bucket** (Fixed Cost, Living Cost, Lifestyle).
- **🏦 Multi-Wallet & Transfer:** Kelola banyak dompet (Cash, Bank, E-Wallet) dan lakukan transfer antar dompet (seperti tarik tunai ATM).
- **⚖️ Cash Opname:** Fitur penyesuaian saldo jika uang fisik tidak sesuai dengan aplikasi (otomatis mencatat selisih).
- **🔒 Secure Session:** Akses aplikasi aman dengan **PIN Keluarga** dan sistem *auto-logout* setiap 1 jam.
- **📱 PWA Ready:** Bisa di-install di HP (Android/iOS) dan terasa seperti aplikasi native tanpa harus melalui App Store.

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI (High Performance)
- **Database:** SQLite (Relational, File-based)
- **ORM:** SQLAlchemy
- **AI:** Google Gemini Pro API (via `google-generativeai`)
- **Frontend:** Jinja2 Templates, Tailwind CSS (via CDN), Chart.js
- **Containerization:** Docker & Docker Compose

## 🚀 Cara Menjalankan (Docker)

Pastikan Anda sudah menginstal Docker di laptop Anda.

1.  **Clone Repositori:**
    ```bash
    git clone https://github.com/inspironCons/family-finance-dons-family.git
    cd family-finance-dons-family
    ```

2.  **Siapkan API Key:**
    Dapatkan API Key Gemini di [Google AI Studio](https://aistudio.google.com/app/apikey).

3.  **Jalankan dengan Docker CLI:**
    ```powershell
    docker build -t finance-pwa .
    docker run -d `
      -p 8000:8000 `
      -v ${PWD}/data:/app/data `
      -e ADMIN_PIN=512323 `
      -e GEMINI_API_KEY="KUNCI_API_ANDA" `
      --name family-finance-app `
      finance-pwa
    ```

4.  **Akses Aplikasi:**
    Buka browser dan ketik: `http://localhost:8000`

## ⚙️ Konfigurasi Environment

| Variabel | Deskripsi | Default |
| :--- | :--- | :--- |
| `ADMIN_PIN` | PIN untuk login aplikasi | `123456` |
| `GEMINI_API_KEY` | API Key dari Google AI Studio | - |
| `SECRET_KEY` | Key untuk enkripsi session cookie | `RAHASIA_SUPER_AMAN` |

## 👨‍👩‍👧 Profil Target Analisa AI
Aplikasi ini dioptimalkan untuk keluarga dengan profil:
- Pekerjaan tetap (Kantoran) + Pengusaha (Fluktuatif).
- Memiliki tanggungan anak usia balita.
- Memiliki target pelunasan KPR dan upgrade aset kendaraan.

---
Dibuat dengan ❤️ untuk kemajuan finansial keluarga.
