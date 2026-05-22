# FASE 6: Otomatisasi Webhook - Google Form → Sheets → ChromaDB

## 📋 Overview

Fase ini mengimplementasikan otomatisasi end-to-end untuk input data skripsi:

```
Google Form → Google Sheets → Google Apps Script → Webhook Server → ChromaDB
```

Sebelumnya, input data masih dilakukan manual via upload file `.xlsx` di UI Streamlit.  
Dengan webhook ini, setiap submission Google Form langsung tersimpan ke ChromaDB secara otomatis.

---

## 📁 File-file Baru

| File | Lokasi | Fungsi |
|------|--------|--------|
| `webhook_server.py` | Root | FastAPI app untuk menerima POST /webhook |
| `apps_script.gs` | Root | Google Apps Script yang dipasang di Google Sheets |
| `requirements.txt` | Root | Dependency baru: fastapi, python-multipart |

---

## 🚀 Setup & Cara Menjalankan

### 1. Update Dependencies

Pastikan dependency baru sudah terinstall:

```bash
# Terminal di root VSS/
pip install -r requirements.txt
```

Dependency baru yang ditambahkan:
- `fastapi==0.115.9` - REST API framework
- `python-multipart==0.0.7` - Form data parsing
- `uvicorn==0.41.0` - ASGI server (sudah ada, tidak perlu install ulang)

### 2. Menjalankan Webhook Server

#### Development Mode (localhost:8000)

```bash
# Terminal di root VSS/
python webhook_server.py
```

Output:
```
[Webhook] Starting VSS Webhook Server...
[Webhook] Docs tersedia di: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Akses:
- **Docs (Swagger UI)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Status**: http://localhost:8000/status (jumlah dokumen di ChromaDB)

#### Production Mode (dengan reverse proxy)

Lihat bagian "Expose ke Internet" di bawah.

---

## 🌐 Expose ke Internet untuk Testing (dengan Ngrok)

Jika ingin test webhook dengan server online (misal dari Google Form production):

### Install Ngrok

```bash
# Download dari https://ngrok.com/download
# Atau via package manager:

# macOS (brew)
brew install ngrok/ngrok/ngrok

# Windows (choco)
choco install ngrok

# Linux (apt)
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok-stable-linux-amd64.tgz | tar xz sudo mv ./ngrok /usr/local/bin
```

### Jalankan Ngrok

**Terminal 1**: Start Webhook Server

```bash
cd d:\.KULIAHKU\Bismillah\vss
python webhook_server.py
```

**Terminal 2**: Expose dengan Ngrok

```bash
ngrok http 8000
```

Output (contoh):
```
ngrok                                   (Ctrl+C to quit)

Session Status                online
Account                       your-email@example.com (Plan: Free)
Version                       3.3.5
Region                        us (United States)
Forwarding                    https://a1b2-34-56-78-90.ngrok.io -> http://localhost:8000
Connections                   ttl    opn    rt1    rt5    p95
                              0      0      0.00s  0.00s  0.00s

```

**Catat URL**: `https://a1b2-34-56-78-90.ngrok.io` (ini adalah PUBLIC WEBHOOK_URL Anda)

### Test dengan Curl

```bash
curl -X POST "https://a1b2-34-56-78-90.ngrok.io/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Ahmad Ridho",
    "jurusan": "Teknik Informatika",
    "judul": "Sistem Deteksi Kemiripan Judul Tugas Akhir",
    "abstrak": "Penelitian ini mengembangkan sistem berbasis vektor embedding untuk mendeteksi kemiripan judul TA...",
    "tahun": "2024"
  }'
```

Expected Response:
```json
{
  "status": "success",
  "id": "doc_20250519_143022_a1b2c3d4",
  "pesan": "Dokumen 'Sistem Deteksi Kemiripan Judul Tugas Akhir' berhasil disimpan ke ChromaDB"
}
```

---

## 📝 Cara Pasang Google Apps Script

### Step 1: Siapkan Google Form dan Google Sheet

1. **Buat Google Form** dengan pertanyaan:
   - Nama Mahasiswa (short answer)
   - Jurusan/Program Studi (short answer)
   - Judul Skripsi (long answer)
   - Abstrak Skripsi (long answer)
   - Tahun Akademik (short answer)

2. **Hubungkan Form ke Google Sheet**:
   - Saat membuat form, klik icon "Link to Sheets"
   - Pilih "Create new spreadsheet" atau pilih sheet yang sudah ada
   - Sheet akan otomatis menerima response dengan kolom:
     ```
     [0] Timestamp
     [1] Nama Mahasiswa
     [2] Jurusan/Program Studi
     [3] Judul Skripsi
     [4] Abstrak Skripsi
     [5] Tahun Akademik
     ```

### Step 2: Buka Google Apps Script Editor

1. Di Google Sheet response form, klik **Extensions** → **Apps Script**
2. Akan membuka tab baru dengan Google Apps Script editor

### Step 3: Copy Paste apps_script.gs

1. Hapus semua kode default di editor
2. Copy seluruh isi file `apps_script.gs` dari root VSS folder
3. Paste ke editor Google Apps Script
4. **GANTI `WEBHOOK_URL`** dengan URL server Anda:

```javascript
// Untuk development (localhost):
const WEBHOOK_URL = "http://localhost:8000/webhook";

// Atau untuk production (via ngrok atau domain):
const WEBHOOK_URL = "https://a1b2-34-56-78-90.ngrok.io/webhook";

// Atau untuk domain custom:
const WEBHOOK_URL = "https://webhook.yourdomain.com/webhook";
```

5. **Jika nama sheet berbeda**, edit function `getLatestSubmission()`:

```javascript
// Cari baris ini:
const sheet = ss.getSheetByName("Form Responses 1");

// Ganti "Form Responses 1" dengan nama sheet Anda
// (lihat tab name di Google Sheet)
```

6. **Jika urutan kolom berbeda**, edit struktur di `getLatestSubmission()`:

```javascript
// Default asumsi:
// [0] Timestamp, [1] Nama, [2] Jurusan, [3] Judul, [4] Abstrak, [5] Tahun

// Jika kolom berubah, sesuaikan index:
const data = {
  timestamp: row[0] || "",  // Kolom A
  nama: row[1] || "",       // Kolom B
  jurusan: row[2] || "",    // Kolom C
  judul: row[3] || "",      // Kolom D
  abstrak: row[4] || "",    // Kolom E
  tahun: row[5] || "",      // Kolom F
};
```

7. Simpan file dengan **Ctrl+S** atau **File → Save**

### Step 4: Set Trigger untuk onFormSubmit

1. Di editor Google Apps Script, klik tombol **"⏰" (Triggers)** di sebelah kiri
2. Atau: **Run → Add a trigger** atau **Execution → All executions**
3. Klik **"+ Create new trigger"** (pojok bawah kanan)
4. Atur trigger:
   - **Function**: `onFormSubmit`
   - **Deployment**: Head
   - **Event source**: From spreadsheet
   - **Event type**: **On form submit** ← Penting!
5. Klik **Create**
6. Dialog akan meminta authorization → **Authorize**

### Step 5: Grant Permissions

Google akan meminta izin untuk:
- Akses Google Sheet (read/write)
- Network request (UrlFetchApp)

Klik **Review permissions** → **Authorize with your Google account** → Pilih akun → **Allow**

### Step 6: Verifikasi di Logs

1. Di Google Apps Script editor, buka **View → Logs** atau **Execution → All executions**
2. Submit form baru dan lihat log:

```
[Apps Script] ===== onFormSubmit() triggered =====
[Apps Script] Data submission yang diambil: {"timestamp":"...","nama":"Ahmad","nim":"2024001",...}
[Apps Script] Mengirim ke webhook: http://localhost:8000/webhook
[Apps Script] Payload: {"nama":"Ahmad","nim":"2024001","judul":"..."}
[Apps Script] Response code: 200
[Apps Script] Response body: {"status":"success","id":"doc_...","pesan":"..."}
[Apps Script] ✓ SUCCESS
[Apps Script] Response: {"status":"success","id":"doc_20250519_143022_a1b2c3d4","pesan":"..."}
```

---

## 📱 Switching ke Production

Saat pindah dari development ke server production:

### 1. Ubah WEBHOOK_URL di Apps Script

```javascript
// Development
const WEBHOOK_URL = "http://localhost:8000/webhook";

// Production (ganti dengan domain/IP server)
const WEBHOOK_URL = "https://webhook.yourdomain.com/webhook";
// atau
const WEBHOOK_URL = "https://your-server-ip:8000/webhook";
```

Klik **Save** (Ctrl+S)

### 2. Start Webhook Server di Production

```bash
# Di server production
cd /path/to/vss
python -m uvicorn webhook_server.py:app --host 0.0.0.0 --port 8000

# Atau gunakan process manager (recommended):
# - Systemd (Linux)
# - PM2 (Node.js-like)
# - Supervisor
# - Docker + container orchestration
```

### 3. Setup Reverse Proxy (Nginx/Apache)

Untuk production, gunakan reverse proxy agar HTTPS dan domain custom:

**Nginx** (contoh):
```nginx
server {
    listen 443 ssl http2;
    server_name webhook.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook {
        proxy_pass http://localhost:8000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Verifikasi Connection

Test dengan curl dari production server:

```bash
curl -X GET "https://webhook.yourdomain.com/status" \
  -H "Authorization: Bearer YOUR_TOKEN" # jika ada authentication
```

---

## ✅ Cara Verifikasi Data Masuk ke ChromaDB

### 1. Cek via API `/status` Endpoint

```bash
curl http://localhost:8000/status
```

Response:
```json
{
  "status": "ok",
  "total_documents": 45  // Total dokumen di ChromaDB
}
```

### 2. Cek via Python REPL

```python
from modules.database import VectorDatabase

db = VectorDatabase()
count = db.count()
print(f"Total dokumen: {count}")

# Ambil semua dokumen
all_docs = db.get_all()
print(all_docs)
```

### 3. Cek via Streamlit UI

Jalankan aplikasi Streamlit dan cari dokumen yang baru disimpan:

```bash
streamlit run app.py
```

Cari di search bar menggunakan judul atau kata kunci abstrak dari submission Google Form terbaru.

### 4. Cek via ChromaDB CLI (opsional)

```bash
# Install chroma cli
pip install chroma-db

# Query collection
chroma describe skripsi_embeddings
```

---

## 🔍 Troubleshooting

### Error: "Sheet 'Form Responses 1' tidak ditemukan"

**Penyebab**: Nama sheet default Google Form berbeda.

**Solusi**:
1. Buka Google Sheet dan cek nama tab response sheet (bukan "Form Responses 1"?)
2. Edit `apps_script.gs` baris ini:
   ```javascript
   const sheet = ss.getSheetByName("NAMA_SHEET_YANG_BENAR");
   ```
3. Save dan coba again.

### Error: "ERROR saat fetch ke webhook"

**Penyebab**:
- Server webhook tidak running
- WEBHOOK_URL salah
- Firewall/network issue
- CORS issue

**Solusi**:
1. Pastikan `python webhook_server.py` sedang jalan di terminal 1
2. Pastikan WEBHOOK_URL di apps_script.gs sudah benar (sesuai dengan URL server)
3. Test endpoint secara manual dengan curl atau Postman
4. Cek logs di Google Apps Script: **View → Logs**

### Error: "CORS issue"

**Penyebab**: Jika from domain berbeda.

**Solusi**:
Apps Script sudah handle CORS, tapi jika tetap error, tambahkan di webhook_server.py:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Dokumen tidak masuk ke ChromaDB

**Checklist**:
1. ✅ Webhook server sedang running?
2. ✅ WEBHOOK_URL sudah benar?
3. ✅ Trigger `onFormSubmit` sudah di-set?
4. ✅ Authorization sudah di-grant?
5. ✅ Cek logs di Google Apps Script (View → Logs)
6. ✅ Cek logs di terminal webhook server (stdout/stderr)
7. ✅ ChromaDB path (`./chroma_db/`) accessible?

### Masalah: Dokumen di ChromaDB tapi tidak muncul di search (RESOLVED ✅)

**Gejala**: 
- Webhook berhasil (200 OK), dokumen masuk ChromaDB
- Tetapi saat search di Streamlit, judul tidak muncul
- Field "Mahasiswa" dan "Prodi" menampilkan "-"

**Penyebab**: 
Field name mismatch antara metadata webhook dan yang dicari searcher:
- Webhook menyimpan: `nama`, `jurusan`
- Searcher mencari: `mahasiswa`, `prodi`

**Solusi** (sudah applied):
1. **modules/searcher.py** - Updated field mapping:
   ```python
   "mahasiswa": metadata.get("nama", metadata.get("mahasiswa", "-")),  # Map 'nama' from webhook
   "prodi": metadata.get("jurusan", metadata.get("prodi", "-")),       # Map 'jurusan' from webhook
   ```

2. **app.py** - Updated table display:
   ```python
   "Mahasiswa": m.get("nama", m.get("mahasiswa", "-")),  # Map 'nama' from webhook
   "Prodi": m.get("jurusan", m.get("prodi", "-"))        # Map 'jurusan' from webhook
   ```

**Verifikasi**:
```bash
# Search sekarang bekerja dengan data webhook
python -c "
from modules.searcher import Searcher
searcher = Searcher()
results = searcher.search('deteksi kemiripan', top_n=3)
for r in results:
    print(f'{r[\"judul\"][:60]}... | {r[\"mahasiswa\"]} | {r[\"prodi\"]} | {r[\"similarity\"]:.0%}')
"
```

Expected output:
```
Sistem Deteksi Kemiripan... | magfirah suhama | Sistem Informasi | 49%
```

---

## 📊 Schema & Payload Reference

### Request Body (POST /webhook)

```json
{
  "nama": "Ahmad Ridho",
  "jurusan": "Teknik Informatika",
  "judul": "Sistem Deteksi Kemiripan Judul Tugas Akhir menggunakan Vector Embedding",
  "abstrak": "Penelitian ini mengembangkan sistem yang dapat mendeteksi tingkat kemiripan antara judul-judul tugas akhir menggunakan teknik vector embedding dengan model BAAI/bge-m3...",
  "tahun": "2024"
}
```

### Response Body (200 OK)

```json
{
  "status": "success",
  "id": "doc_20250519_143022_a1b2c3d4",
  "pesan": "Dokumen 'Sistem Deteksi Kemiripan Judul Tugas Akhir menggunakan Vector Embedding' berhasil disimpan ke ChromaDB"
}
```

### Response Body (Error)

```json
{
  "detail": "Judul tidak boleh kosong"  // 400 Bad Request
}
```

atau

```json
{
  "detail": "Internal server error: ..."  // 500 Internal Server Error
}
```

---

## 📚 Arsitektur Data Flow

```
┌─────────────────┐
│  Google Form    │ (UI untuk input data)
└────────┬────────┘
         │
         │ Submit
         ↓
┌─────────────────────────────┐
│  Google Sheets              │ (Response store)
│  [Timestamp|Nama|NIM|...]   │
└────────┬────────────────────┘
         │
         │ Form Submit Trigger
         ↓
┌─────────────────────────────┐
│  Google Apps Script         │ (apps_script.gs)
│  - Read row data            │
│  - Validate fields          │
│  - POST JSON to webhook     │
└────────┬────────────────────┘
         │
         │ HTTP POST JSON
         │
         ↓
┌──────────────────────────────────┐
│  Webhook Server (FastAPI)        │ (webhook_server.py)
│  POST /webhook                   │
│  - Validate input                │
│  - Preprocessing (combine_title  │
│    + abstrak)                    │
│  - Embedding (bge-m3)            │
│  - Metadata prep                 │
│  - Insert to ChromaDB            │
└────────┬─────────────────────────┘
         │
         │ write
         ↓
┌──────────────────────────────────┐
│  ChromaDB (Persistent)           │
│  Collection: skripsi_embeddings  │
│  - doc_id                        │
│  - embedding (1024-dim)          │
│  - metadata {nama, nim, ...}     │
└──────────────────────────────────┘
         │
         │ query
         ↓
┌──────────────────────────────────┐
│  Streamlit UI (app.py)           │
│  - Search similarity             │
│  - Display results               │
└──────────────────────────────────┘
```

---

## 📖 Referensi

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Google Apps Script Docs**: https://developers.google.com/apps-script
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
- **Ngrok Docs**: https://ngrok.com/docs

---

## 🎯 Next Steps (Opsional)

1. **Authentication**: Tambahkan API key validation di webhook
2. **Rate Limiting**: Cegah abuse dengan rate limiter
3. **Database Backup**: Schedule backup chroma_db ke cloud storage
4. **Monitoring**: Setup alert saat webhook error
5. **Queue System**: Gunakan Celery/RQ untuk async processing jika volume besar
6. **WebSocket**: Real-time notification saat dokumen berhasil masuk

---

**Last Updated**: May 19, 2025  
**Author**: VSS Development Team
