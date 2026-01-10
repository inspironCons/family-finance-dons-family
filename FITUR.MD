# Spesifikasi Fitur: Family Finance PWA
**Versi:** 1.0  
**Tipe:** Personal Family Finance (Strict & Detailed)  
**Platform:** Progressive Web App (Mobile First)  
**Tech Stack:** Python FastAPI, SQLite, Jinja2, Tailwind CSS

---

## 1. Dashboard Utama (Financial Cockpit)
*Halaman pendaratan saat aplikasi dibuka. Memberikan status kesehatan finansial dalam 5 detik pertama.*

### A. Kartu Status Likuiditas (Real-time)
Menampilkan total uang tunai/digital yang siap digunakan.
- **Total Saldo:** `SUM(All Wallets)`
- **Breakdown:**
    - Cash (Dompet Fisik)
    - Bank (BCA/Mandiri)
    - E-Wallet (Gopay/OVO)

### B. Indikator "Runway" Bulan Ini
Visualisasi keamanan budget operasional.
- **Progress Bar:** Menunjukkan persentase pengeluaran vs pemasukan.
- **Logic Indikator Warna:**
    - 🟢 **Hijau:** Pengeluaran < 50% (Aman)
    - 🟡 **Kuning:** Pengeluaran 50% - 80% (Waspada)
    - 🔴 **Merah:** Pengeluaran > 80% (Bahaya/Stop Jajan)

### C. Smart Daily Allowance (Jatah Harian)
Psikologi untuk mengerem pengeluaran harian.
- **Formula:** `(Sisa Income - Total Fixed Cost - Tabungan Wajib) / Sisa Hari dalam Bulan`
- **Tampilan:** "Jatah aman jajan hari ini: **Rp 150.000**"

---

## 2. Manajemen Transaksi (Cermat & Teliti)
*Input data harus cepat, namun pengelompokan di backend harus detail.*

### A. Input Transaksi Cepat (Fast Action)
- **Tombol Floating (FAB):** (+) Besar di pojok kanan bawah.
- **Form Input:**
    - Tanggal (Default: Hari ini)
    - Nominal
    - Kategori (Dropdown)
    - Dompet Sumber (Dropdown)
    - Catatan/Deskripsi
    - Foto Struk (Opsional, kompresi otomatis)

### B. Pengelompokan Prioritas (The 3 Buckets)
Setiap kategori pengeluaran harus di-tag ke salah satu grup ini:
1.  **Fixed Cost (Kewajiban):** KPR, Listrik, SPP, Gaji ART.
2.  **Living Cost (Kebutuhan):** Belanja Pasar, Susu/Popok Anak, Transport.
3.  **Lifestyle (Keinginan):** Makan Luar, Kopi, Hobi, Hiburan.

---

## 3. Modul Laporan & Analisa (Report)
*Fitur "Detektif" untuk melacak kebocoran anggaran.*

### A. Cashflow Statement
- Pemasukan vs Pengeluaran per bulan.
- Net Cashflow (Surplus/Defisit).

### B. Analisa Kategori (Pie Chart)
- Visualisasi persentase pengeluaran per kategori.
- *Insight Text:* "Bulan ini pengeluaran terbesar ada di **Belanja Pasar (40%)**."

### C. Analisa Tren (Month-to-Month)
- Membandingkan pos pengeluaran spesifik dengan bulan lalu.
- **Indikator:**
    - ⬆️ "Listrik naik 15% dibanding bulan lalu"
    - ⬇️ "Jajan luar turun 20%"

### D. Deteksi "Bocor Alus" (Frequency Tracker)
- Menghitung frekuensi transaksi kategori Lifestyle.
- *Contoh:* "Anda membeli Kopi **12x** bulan ini total **Rp 360.000**."

---

## 4. Manajemen Aset & Tujuan (Goals)
*Melihat gambaran besar kekayaan, bukan hanya cashflow bulanan.*

### A. Dana Darurat Tracker
- Target vs Aktual.
- Estimasi berapa bulan lagi target tercapai dengan *saving rate* saat ini.

### B. Sinking Funds (Pos Terencana)
Amplop virtual untuk pengeluaran tahunan.
- **List:** Pajak Kendaraan, Kurban, Mudik Lebaran, Servis Mobil.
- **Logika:** Saldo ini tidak boleh dianggap sebagai "Uang Nganggur".

### C. Pos Anak
- Tracking biaya spesifik anak (Imunisasi, Susu, Tabungan Sekolah).

---

## 5. Kalender Tagihan (Bill Reminder)
*Mencegah denda keterlambatan.*

- **List View:** Daftar tagihan berulang.
- **Status:** `Paid` (Hijau) / `Unpaid` (Merah).
- **Due Date Alert:** Highlight merah jika H-3 jatuh tempo.
- **Total Kewajiban Tertunda:** Jumlah uang yang harus disisihkan detik ini untuk bayar tagihan sisa bulan ini.

---

## 6. Spesifikasi Teknis (PWA Focus)

### Responsiveness (Tailwind Classes)
- **Mobile:**
    - Navigasi: `fixed bottom-0 w-full` (Bottom Bar).
    - Tabel Laporan: `hidden` (Ganti dengan Card View).
    - Font Size: Minimal `text-base` agar terbaca jelas.
- **Desktop:**
    - Navigasi: Sidebar atau Topbar.
    - Tabel Laporan: Full `table-auto` dengan detail lengkap.

### Offline Capability
- **Service Worker:** Cache halaman utama (Dashboard & Input) agar bisa dibuka saat sinyal hilang (offline mode).
- **Manifest:** `display: standalone` untuk menghilangkan browser bar.

### Database Schema (SQLite)
Secara garis besar tabel yang dibutuhkan:
1.  `users` (id, name, pin)
2.  `wallets` (id, name, type, initial_balance)
3.  `categories` (id, name, type, priority_group [Fixed/Living/Lifestyle])
4.  `transactions` (id, date, amount, wallet_id, category_id, description, receipt_path)
5.  `budgets` (id, category_id, amount_limit, month_period)