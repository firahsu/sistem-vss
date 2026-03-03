# ✅ FASE 5 — Integrasi, Testing & Finalisasi

---

| Field | Detail |
|-------|--------|
| **Fase** | 5 dari 5 (terakhir) |
| **Status** | ⬜ Belum Dimulai |
| **Prasyarat** | [Fase 4](FASE_4_Frontend.md) selesai dan checklist gate terpenuhi |
| **Fase Selanjutnya** | Tidak ada — proyek selesai setelah fase ini |
| **Referensi TRD** | Bagian 8 (Panduan Menjalankan), 8.2 (Incremental Update), 9 (Batasan & Mitigasi) |

> **Tujuan:** Memastikan seluruh sistem bekerja secara end-to-end, menangani edge case, mengimplementasi fitur incremental update, menambahkan disclaimer, dan menyelesaikan dokumentasi akhir.

---

## Navigasi

[← Fase 4](FASE_4_Frontend.md) · [PLANNING](PLANNING.md) · **Fase 5** · [Catatan Revisi](REVISION_NOTES.md)

---

## Daftar Isi Fase 5

1. [Gambaran Testing & Tugas Akhir](#1-gambaran-testing--tugas-akhir)
2. [Bagian A — Testing End-to-End](#2-bagian-a--testing-end-to-end)
3. [Bagian B — Incremental Update](#3-bagian-b--incremental-update)
4. [Bagian C — Finalisasi & Dokumentasi](#4-bagian-c--finalisasi--dokumentasi)
5. [Checklist Final — Proyek Selesai](#5-checklist-final--proyek-selesai)

---

## 1. Gambaran Testing & Tugas Akhir

Fase ini terdiri dari tiga bagian:

```
┌──────────────────────────────────────────────────────────────────┐
│  FASE 5 — Tiga area yang dikerjakan                              │
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────┐ │
│  │   A. Testing E2E   │  │  B. Incremental    │  │ C. Final   │ │
│  │                    │  │     Update         │  │            │ │
│  │ • Restart test     │  │ • Tambah dokumen   │  │ • Discl.   │ │
│  │ • Edge cases       │  │   baru tanpa       │  │ • README   │ │
│  │ • 5 judul uji      │  │   rebuild index    │  │ • req.txt  │ │
│  │ • Stress test      │  │ • Verifikasi       │  │ • Review   │ │
│  └────────────────────┘  └────────────────────┘  └────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Bagian A — Testing End-to-End

### 2.1 Test Persistensi Data

**Tujuan:** Memastikan data di ChromaDB tetap ada setelah program/server dihentikan dan dijalankan ulang.

**Langkah:**

1. Hentikan Streamlit jika sedang berjalan (`Ctrl+C`)
2. Jalankan ulang:
   ```powershell
   streamlit run app.py
   ```
3. Lakukan pencarian — hasil harus muncul seperti sebelumnya

**Verifikasi alternatif via script:**

```python
python -c "
from modules.database import VectorDatabase
db = VectorDatabase()
count = db.count()
assert count > 0, f'Database kosong setelah restart! Count: {count}'
print(f'✅ Data persistent: {count} dokumen tersedia')
"
```

### 2.2 Test dengan 5 Judul Berbeda

Uji sistem dengan 5 judul dari berbagai topik dan catat hasilnya:

| No | Judul Input | Top-1 Hasil | Similarity | Kesesuaian Topik? |
|----|-------------|-------------|------------|-------------------|
| 1 | (isi sendiri — topik machine learning) | | | ☐ Ya ☐ Tidak |
| 2 | (isi sendiri — topik sistem informasi) | | | ☐ Ya ☐ Tidak |
| 3 | (isi sendiri — topik jaringan komputer) | | | ☐ Ya ☐ Tidak |
| 4 | (isi sendiri — topik data mining/analisis data) | | | ☐ Ya ☐ Tidak |
| 5 | (isi sendiri — topik yang tidak ada di dataset) | | | ☐ Ya ☐ Tidak |

> **Catatan:** Isi tabel di atas selama pengujian. Salin ke [REVISION_NOTES.md](REVISION_NOTES.md) sebagai dokumentasi hasil uji.

### 2.3 Test Edge Cases

Uji input-input yang tidak biasa untuk memastikan sistem tidak crash:

#### Edge Case 1: Karakter Spesial

```
Input: "!!!@@@###$$$%%%^^^&&&"
Expected: Sistem tidak crash. Mungkin menampilkan hasil dengan similarity rendah.
```

#### Edge Case 2: Input Sangat Pendek

```
Input: "AI"
Expected: Sistem berjalan normal, menampilkan hasil.
```

#### Edge Case 3: Input Sangat Panjang

```
Input: (Salin sebuah paragraf panjang >200 kata)
Expected: Sistem berjalan normal, menampilkan hasil.
```

#### Edge Case 4: Campuran Bahasa

```
Input: "Implementation of machine learning untuk deteksi anomali"
Expected: Sistem berjalan normal. Model bge-m3 mendukung multilingual.
```

#### Edge Case 5: Hanya Spasi

```
Input: "      "
Expected: Muncul pesan warning (karena strip() menghasilkan string kosong).
```

#### Edge Case 6: Angka Saja

```
Input: "12345 67890"
Expected: Sistem tidak crash. Menampilkan hasil dengan similarity rendah.
```

### Langkah — Checklist Bagian A

- [ ] **5.1** Test persistensi: data tetap ada setelah restart
- [ ] **5.2** Test 5 judul berbeda: hasilnya dicatat di tabel di atas
- [ ] **5.3** Edge case — karakter spesial: tidak crash
- [ ] **5.4** Edge case — input pendek: tidak crash
- [ ] **5.5** Edge case — input panjang: tidak crash
- [ ] **5.6** Edge case — campuran bahasa: tidak crash
- [ ] **5.7** Edge case — hanya spasi: muncul warning
- [ ] **5.8** Edge case — angka saja: tidak crash

---

## 3. Bagian B — Incremental Update

### 3.1 Tentang Incremental Update

Dari TRD Bagian 8.2: Jika dataset bertambah, **tidak perlu rebuild semua index**. Dokumen baru dapat ditambahkan secara individual menggunakan fungsi insert.

### 3.2 Cara Menambah Dokumen Baru

Buat script atau jalankan di Python interpreter:

```python
from modules.preprocessor import combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase

# Inisialisasi
embedder = Embedder()
db = VectorDatabase()

# Data dokumen baru
new_title    = 'Judul tugas akhir baru yang akan ditambahkan'
new_abstract = 'Abstrak lengkap dari tugas akhir baru ini menjelaskan tentang...'
new_metadata = {
    'judul'     : new_title,
    'mahasiswa' : 'Nama Mahasiswa Baru',
    'tahun'     : '2025',
    'prodi'     : 'Teknik Informatika'
}

# Proses: gabung + preprocess + embed + simpan
combined  = combine_title_abstract(new_title, new_abstract)
embedding = embedder.embed(combined)

# Gunakan ID unik (pastikan tidak duplikat!)
new_id = f'doc_{db.count()}'  # Atau gunakan NIM/ID unik lainnya
db.insert(doc_id=new_id, embedding=embedding, metadata=new_metadata)

print(f'Dokumen ditambahkan. Total sekarang: {db.count()}')
```

### 3.3 Pengujian Incremental Update

```python
python -c "
from modules.preprocessor import combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase
from modules.searcher import Searcher

embedder = Embedder()
db = VectorDatabase()

# Catat jumlah awal
count_before = db.count()
print(f'Dokumen sebelum: {count_before}')

# Tambah dokumen baru
title = 'Pengembangan Aplikasi Mobile untuk Monitoring Kesehatan Pasien'
abstract = 'Aplikasi mobile berbasis Android dikembangkan untuk membantu monitoring kesehatan pasien secara real-time menggunakan sensor IoT.'
metadata = {'judul': title, 'mahasiswa': 'Test User', 'tahun': '2025', 'prodi': 'TI'}

combined = combine_title_abstract(title, abstract)
embedding = embedder.embed(combined)
db.insert(f'doc_test_incr', embedding, metadata)

# Verifikasi jumlah bertambah
count_after = db.count()
print(f'Dokumen setelah: {count_after}')
assert count_after == count_before + 1, 'Jumlah tidak bertambah!'

# Cari dokumen yang baru ditambahkan
searcher = Searcher()
results = searcher.search('aplikasi mobile monitoring kesehatan', top_n=3)
print(f'\\nHasil pencarian setelah incremental update:')
for i, r in enumerate(results):
    print(f'  {i+1}. [{r[\"similarity\"]:.4f}] {r[\"judul\"]}')

# Dokumen baru HARUS muncul di hasil (karena query sangat mirip)
found = any('Monitoring Kesehatan' in r['judul'] for r in results)
assert found, 'Dokumen baru tidak ditemukan di hasil pencarian!'

print('\\n✅ Incremental update berhasil!')
"
```

> **⚠️ Perhatian ID Duplikat:** Jika Anda menjalankan test incremental berulang kali, gunakan ID berbeda atau hapus dokumen test sebelumnya. ChromaDB akan error jika ada ID duplikat.

### Langkah — Checklist Bagian B

- [ ] **5.9** Berhasil menambah dokumen baru tanpa error
- [ ] **5.10** `db.count()` bertambah setelah insert
- [ ] **5.11** Dokumen baru muncul di hasil pencarian

---

## 4. Bagian C — Finalisasi & Dokumentasi

### 4.1 Tambahkan Disclaimer di UI

Dari TRD Bagian 9: Sistem ini **bukan plagiarism checker**. Tambahkan disclaimer di `app.py`.

**Tambahkan di bagian bawah `app.py`** (setelah tabel hasil atau di bagian footer):

```python
# Tambahkan di bagian paling bawah app.py

st.divider()
st.caption(
    '⚠️ **Disclaimer:** Sistem ini merupakan alat bantu validasi kemiripan topik, '
    'bukan plagiarism checker. Hasil similarity menunjukkan kedekatan semantik judul, '
    'bukan kesamaan isi dokumen secara keseluruhan. Keputusan akhir tetap berada '
    'pada dosen pembimbing/penguji.'
)
```

### 4.2 Perbarui `README.md`

Update `README.md` dengan instruksi lengkap:

```markdown
# Sistem Deteksi Kemiripan Judul Tugas Akhir

Sistem berbasis Vector Similarity Search untuk membantu dosen memvalidasi
kemiripan topik sebelum ACC judul tugas akhir.

## Stack Teknologi
- **Python** 3.10/3.11
- **Model Embedding:** BAAI/bge-m3 (via SentenceTransformers)
- **Vector Database:** ChromaDB (persistent storage)
- **Frontend:** Streamlit
- **GPU:** NVIDIA RTX (CUDA-compatible)

## Cara Setup Pertama Kali

1. Buat dan aktifkan virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   ```

2. Install dependencies:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   pip install -r requirements.txt
   ```

3. Siapkan dataset di `data/dataset.xlsx` dengan kolom: `judul`, `abstrak`, `mahasiswa`, `tahun`, `prodi`

4. Jalankan indexer (satu kali):
   ```bash
   python -m modules.indexer
   ```

5. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

6. Buka browser ke `http://localhost:8501`

## Menambah Dokumen Baru

Tidak perlu rebuild index. Gunakan script incremental insert:

```python
from modules.preprocessor import combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase

embedder = Embedder()
db = VectorDatabase()

combined = combine_title_abstract('Judul Baru', 'Abstrak baru...')
embedding = embedder.embed(combined)
db.insert('doc_id_unik', embedding, {'judul': 'Judul Baru', 'mahasiswa': '...', 'tahun': '...', 'prodi': '...'})
```

## Struktur Proyek

```
skripsi-similarity/
├── app.py                  # Streamlit UI
├── modules/
│   ├── preprocessor.py     # Preprocessing teks
│   ├── embedder.py         # Model embedding bge-m3
│   ├── database.py         # ChromaDB wrapper
│   ├── searcher.py         # Logika pencarian
│   └── indexer.py          # Indexing dataset
├── data/
│   └── dataset.xlsx        # Dataset judul + abstrak
├── chroma_db/              # Vector database (auto-generated)
└── requirements.txt
```

## Disclaimer

Sistem ini merupakan alat bantu validasi kemiripan topik, bukan plagiarism checker.
Hasil similarity menunjukkan kedekatan semantik judul, bukan kesamaan isi dokumen.
```

### 4.3 Finalisasi `requirements.txt`

Pastikan `requirements.txt` mencerminkan semua library yang benar-benar digunakan:

```powershell
# Cek versi aktual yang terinstall
pip freeze | Select-String "torch|sentence-transformers|chromadb|streamlit|pandas|openpyxl|numpy"
```

Update versi di `requirements.txt` jika perlu.

### 4.4 Review REVISION_NOTES.md

Buka [REVISION_NOTES.md](REVISION_NOTES.md) dan:

1. Tinjau semua catatan yang masih berstatus ⬜ Baru atau 🔄 Sedang Ditangani
2. Selesaikan yang bisa diselesaikan
3. Untuk yang tidak bisa/tidak perlu diselesaikan, ubah status ke ❌ Ditolak dengan alasan
4. Pastikan semua entri memiliki resolusi

### Langkah — Checklist Bagian C

- [ ] **5.12** Disclaimer ditambahkan di `app.py`
- [ ] **5.13** `README.md` diperbarui dengan instruksi lengkap
- [ ] **5.14** `requirements.txt` sesuai dengan library yang terinstall
- [ ] **5.15** Semua catatan di `REVISION_NOTES.md` sudah ditindaklanjuti

---

## 5. Checklist Final — Proyek Selesai

> **🎓 Checklist ini menandakan bahwa seluruh proyek telah selesai.**
>
> Pastikan SEMUA item tercentang sebelum menganggap proyek selesai.

### Fungsionalitas Inti

- [ ] Indexing dataset ke ChromaDB berjalan tanpa error
- [ ] Pencarian kemiripan judul menghasilkan hasil yang masuk akal
- [ ] Similarity score berada di rentang 0.0 – 1.0
- [ ] Hasil terurut dari tertinggi ke terendah

### Persistensi & Reliability

- [ ] Data tetap ada setelah restart program
- [ ] Incremental update (tambah dokumen baru) berfungsi
- [ ] Edge cases tidak menyebabkan crash

### Antarmuka Pengguna

- [ ] Streamlit UI berjalan dan dapat diakses di browser
- [ ] Input, slider, dan tombol berfungsi dengan benar
- [ ] Tabel hasil menampilkan gradient warna pada Similarity
- [ ] Disclaimer ditampilkan di halaman

### Dokumentasi

- [ ] `README.md` berisi instruksi lengkap
- [ ] `requirements.txt` final dan akurat
- [ ] Semua catatan di `REVISION_NOTES.md` sudah di-review

### Semua Fase Selesai

- [ ] [Fase 1](FASE_1_Setup_Environment.md) — Setup Environment ✅
- [ ] [Fase 2](FASE_2_Backend_Core.md) — Backend Core ✅
- [ ] [Fase 3](FASE_3_Logic_Layer.md) — Logic Layer ✅
- [ ] [Fase 4](FASE_4_Frontend.md) — Frontend ✅
- [ ] [Fase 5](FASE_5_Integrasi_Testing.md) — Integrasi & Testing ✅

---

### 🎉 Verifikasi Akhir

Jalankan alur lengkap untuk memastikan semuanya berfungsi:

```powershell
# 1. Aktifkan venv
.\venv\Scripts\Activate.ps1

# 2. Verifikasi database
python -c "from modules.database import VectorDatabase; db = VectorDatabase(); print(f'Database: {db.count()} dokumen')"

# 3. Verifikasi pencarian
python -c "from modules.searcher import Searcher; s = Searcher(); r = s.search('test', top_n=1); print(f'Pencarian berfungsi: {r[0][\"similarity\"]:.4f}')"

# 4. Jalankan aplikasi
streamlit run app.py
```

---

> **🎓 Selamat! Proyek Sistem Deteksi Kemiripan Judul TA telah selesai.**
>
> Kembali ke → [PLANNING.md](PLANNING.md) untuk update status keseluruhan.

---

*Referensi: TRD-SKTA-2025 Bagian 8, 9, dan 10*
