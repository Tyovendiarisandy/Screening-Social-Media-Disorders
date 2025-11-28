# 🧠 SMDS-27 Screening Application

Aplikasi skrining kecanduan media sosial berbasis **Social Media Disorder Scale - 27 Items (SMDS-27)** menggunakan Streamlit, Google Sheets API, dan Gemini AI.

## 🎯 Fitur Utama

1. **Pengumpulan Data Profil** - Nama alias, umur, gender, pekerjaan
2. **Kuesioner SMDS-27** - 27 items dengan skala Likert (0-4)
3. **Penyimpanan Otomatis** - Data disimpan ke Google Sheets
4. **Analisis AI Berbasis Riset** - Menggunakan Gemini 1.5 Pro dengan kriteria strict:
   - Hanya menggunakan artikel ilmiah peer-reviewed
   - Rekomendasi dipersonalisasi sesuai profil user
   - Kesimpulan actionable berbasis bukti ilmiah
   - Menyertakan URL referensi artikel ilmiah

## 📋 Persyaratan

- Python 3.8+
- Google Cloud Project dengan:
  - Google Sheets API enabled
  - Google Drive API enabled
  - Service Account credentials
- Gemini API Key dari Google AI Studio
- Google Sheets untuk menyimpan data

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/username/smds27-screening-app.git
cd smds27-screening-app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Google Cloud Project

#### a. Buat Project di Google Cloud Console
1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru
3. Enable API:
   - Google Sheets API
   - Google Drive API

#### b. Buat Service Account
1. Pergi ke **IAM & Admin** > **Service Accounts**
2. Klik **Create Service Account**
3. Beri nama dan klik **Create**
4. Skip optional steps
5. Klik pada service account yang dibuat
6. Pergi ke tab **Keys**
7. Klik **Add Key** > **Create New Key** > **JSON**
8. Download file JSON credentials

#### c. Setup Google Sheets
1. Buat Google Sheets baru
2. Buat sheet dengan nama **"Responses"**
3. Share sheet dengan email service account (dengan akses **Editor**)
4. Copy Sheet ID dari URL (bagian antara `/d/` dan `/edit`)

### 4. Setup Gemini API

1. Buka [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Klik **Get API Key**
3. Copy API key yang digenerate

### 5. Konfigurasi Secrets

Buat file `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` dan isi dengan kredensial Anda:
```toml
GEMINI_API_KEY = "your-actual-gemini-api-key"
GOOGLE_SHEET_ID = "your-actual-sheet-id"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id-from-json"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-actual-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs/..."
```

### 6. Initialize Google Sheets Headers

Jalankan script Python berikut untuk membuat header di Google Sheets:
```python
from utils.google_sheets import GoogleSheetsManager

manager = GoogleSheetsManager()
manager.initialize_sheet_headers()
print("Headers created successfully!")
```

## 🏃 Menjalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## 📁 Struktur Project
```
smds27-screening-app/
├── .streamlit/
│   ├── secrets.toml          # Kredensial (jangan commit!)
│   └── secrets.toml.example  # Template
├── utils/
│   ├── __init__.py
│   ├── smds_items.py        # Data 27 items SMDS
│   ├── google_sheets.py     # Integrasi Google Sheets
│   └── gemini_analysis.py   # Analisis AI dengan Gemini
├── app.py                   # Main application
├── requirements.txt         # Dependencies
├── .gitignore              # Files to ignore
└── README.md               # Dokumentasi ini
```

## 🔬 Tentang SMDS-27

Social Media Disorder Scale (SMDS) adalah instrumen skrining yang dikembangkan oleh van den Eijnden et al. (2016) untuk mengukur gangguan penggunaan media sosial berdasarkan 9 kriteria DSM-5:

1. **Preoccupation** - Terus memikirkan media sosial
2. **Tolerance** - Butuh waktu lebih banyak untuk puas
3. **Withdrawal** - Tidak nyaman saat tidak bisa akses
4. **Persistence** - Gagal mengontrol penggunaan
5. **Escape** - Menggunakan untuk menghindari masalah
6. **Problems** - Menyebabkan konflik relasional
7. **Displacement** - Mengabaikan aktivitas penting
8. **Deception** - Berbohong tentang penggunaan
9. **Conflict** - Masalah interpersonal

Setiap dimensi diukur dengan 3 items (total 27 items) menggunakan skala Likert 0-4.

## 📊 Interpretasi Skor

- **0-27**: Rendah - Penggunaan normal
- **28-54**: Sedang - Penggunaan bermasalah
- **55-81**: Tinggi - Tanda kecanduan signifikan
- **82-108**: Sangat Tinggi - Kecanduan serius

## 🤖 Analisis AI

Aplikasi menggunakan Gemini 1.5 Pro untuk memberikan:
- Analisis mendalam berdasarkan artikel ilmiah peer-reviewed
- Rekomendasi personal sesuai profil dan pola penggunaan
- Langkah tindak lanjut yang actionable
- Referensi artikel ilmiah dengan URL lengkap

## ⚠️ Disclaimer

Aplikasi ini adalah alat skrining dan **bukan diagnosis klinis**. Hasil skrining bersifat informatif dan sebaiknya dikonsultasikan dengan profesional (psikolog/psikiater) jika menunjukkan hasil yang mengkhawatirkan.

## 📚 Referensi

Van den Eijnden, R. J., Lemmens, J. S., & Valkenburg, P. M. (2016). The Social Media Disorder Scale. *Computers in Human Behavior*, 61, 478-487.

## 📝 Lisensi

Untuk keperluan penelitian dan edukasi.

## 👨‍💻 Kontribusi

Kontribusi sangat diterima! Silakan buat issue atau pull request.

## 📞 Kontak & Dukungan

Jika Anda atau seseorang yang Anda kenal memerlukan bantuan:
- **Halo Kemkes**: 119 ext 8
- **Sejiwa**: 119 ext 8  
- **Into The Light**: @intothelightid (Instagram)

---

**Dibuat dengan ❤️ menggunakan Streamlit, Google Cloud, dan Gemini AI**
