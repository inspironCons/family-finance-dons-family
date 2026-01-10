# Technical Architecture: Family Finance PWA

**Project Name:** Family Finance Tracker  
**Type:** Monolithic Progressive Web App (SSR)  
**Language:** Python 3.10+  
**Status:** Design Phase

---

## 1. Architectural Overview
Aplikasi ini menggunakan pendekatan **Monolithic Server-Side Rendering (SSR)**.
Logika bisnis, pemrosesan data, dan *rendering* tampilan (HTML) dilakukan terpusat di server menggunakan Python. Browser klien (HP/Laptop) hanya menerima HTML matang dan asset statis, menjadikan aplikasi sangat ringan dan cepat.

**Flow:**
`User (Browser)` ↔ `Nginx/Uvicorn` ↔ `FastAPI (Python)` ↔ `SQLite (File System)`

---

## 2. Technology Stack

### A. Backend Core (The Brain)
* **Language:** **Python 3.10+**
    * Dipilih karena ekosistem data analysis yang kuat.
* **Web Framework:** **FastAPI**
    * *Role:* Routing, Request Handling, Validation (`Pydantic`), dan Response rendering.
* **Server:** **Uvicorn**
    * *Role:* ASGI Server untuk menjalankan FastAPI.

### B. Data Layer (The Vault)
* **Database:** **SQLite** (`finance.db`)
    * *Role:* Penyimpanan data transaksional.
    * *Why:* Zero-config, file-based (mudah backup), ACID compliant.
* **ORM:** **SQLAlchemy**
    * *Role:* Abstraksi database. Mengubah Class Python menjadi Table SQL.
* **Data Analysis:** **Pandas**
    * *Role:* Melakukan agregasi kompleks (Grouping, Pivot, Time-series analysis) untuk laporan bulanan. Jauh lebih *maintainable* daripada raw SQL query yang rumit.

### C. Frontend Layer (The Face)
* **Templating Engine:** **Jinja2**
    * *Role:* Merender HTML dinamis dengan data dari backend.
* **CSS Framework:** **Tailwind CSS** (via CDN)
    * *Role:* Utility-first CSS untuk styling cepat dan Responsiveness (Mobile vs Desktop).
* **Icons:** **Phosphor Icons** (via CDN)
    * *Role:* UI Icons (Home, Wallet, Chart).
* **Charting:** **Chart.js**
    * *Role:* Visualisasi data (Pie Chart, Bar Chart) di sisi klien.

### D. PWA Capabilities (The Native Feel)
* **Manifest.json:** Mengatur identitas aplikasi (Nama, Icon, Orientasi).
* **Service Worker (`sw.js`):** Mengatur caching asset statis agar aplikasi bisa dimuat instan (offline support basic).
* **Meta Viewport:** Konfigurasi skala layar untuk iOS dan Android.

---

## 3. Project Structure
Struktur folder dirancang agar modular namun tetap sederhana.

```text
/family-finance-pwa
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Settings (Env vars)
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models.py            # Definisi Tabel Database
│   ├── crud.py              # Logic Create, Read, Update, Delete
│   ├── schemas.py           # Pydantic models (Validasi input)
│   └── routers/             # Pemisahan logic per fitur
│       ├── dashboard.py
│       ├── transactions.py
│       └── reports.py
├── data/
│   └── finance.db           # File Database (Git Ignore)
├── static/
│   ├── css/                 # Custom CSS (jika perlu override Tailwind)
│   ├── js/
│   │   └── sw.js            # Service Worker script
│   ├── img/
│   │   └── icons/           # PWA Icons (192x192, 512x512)
│   └── manifest.json        # PWA Manifest
├── templates/               # Jinja2 HTML files
│   ├── base.html            # Layout utama (Navbar, Footer)
│   ├── components/          # Potongan UI (Cards, List Items)
│   ├── dashboard.