# 📋 PLANNING — Sistem Deteksi Kemiripan Judul TA
### Berdasarkan TRD-SKTA-2025

---

> **Petunjuk Penggunaan:**
> - Kerjakan fase secara **berurutan** (Fase 1 → 2 → 3 → 4 → 5)
> - Sebelum berpindah ke fase berikutnya, **semua item checklist** di fase sebelumnya harus tercentang ✅
> - Gunakan `[x]` untuk menandai item selesai, `[ ]` untuk yang belum
> - Catat semua saran, revisi, atau temuan di file [`REVISION_NOTES.md`](REVISION_NOTES.md)

---

## Status Keseluruhan

| Fase | Nama | Status |
|------|------|--------|
| 1 | Setup Environment & Struktur Proyek | ⬜ Belum Dimulai |
| 2 | Backend Core (Preprocessing + Embedding + Database) | ⬜ Belum Dimulai |
| 3 | Logic Layer (Indexer + Searcher) | ⬜ Belum Dimulai |
| 4 | Frontend (Streamlit UI) | ⬜ Belum Dimulai |
| 5 | Integrasi, Testing & Finalisasi | ⬜ Belum Dimulai |

> **Legenda Status:** ⬜ Belum Dimulai · 🔄 Sedang Dikerjakan · ✅ Selesai

---

## Fase 1 — Setup Environment & Struktur Proyek

**Tujuan:** Menyiapkan lingkungan kerja, virtual environment, semua dependensi, dan struktur folder proyek agar siap untuk implementasi.

**Referensi TRD:** Bagian 3 (Setup Environment) dan Bagian 4.1 (Struktur Direktori Proyek)

### Langkah-langkah

- [ ] **1.1** Buat folder proyek `skripsi-similarity/` sesuai struktur di TRD Bagian 4.1
  ```
  skripsi-similarity/
  ├── app.py
  ├── modules/
  │   ├── __init__.py
  │   ├── preprocessor.py
  │   ├── embedder.py
  │   ├── database.py
  │   ├── searcher.py
  │   └── indexer.py
  ├── data/
  ├── chroma_db/
  ├── requirements.txt
  └── README.md
  ```
- [ ] **1.2** Buat virtual environment (`python -m venv venv`) dan pastikan berhasil diaktivasi
- [ ] **1.3** Verifikasi versi Python (`python --version`) → harus 3.10 atau 3.11
- [ ] **1.4** Install CUDA Toolkit dan verifikasi dengan `nvidia-smi` dan `nvcc --version`
- [ ] **1.5** Install PyTorch dengan CUDA support dan verifikasi GPU terdeteksi:
  ```python
  import torch
  print(torch.cuda.is_available())  # → True
  print(torch.cuda.get_device_name(0))
  ```
- [ ] **1.6** Install semua library utama (`sentence-transformers`, `chromadb`, `streamlit`, `pandas`, `openpyxl`, `numpy`)
- [ ] **1.7** Buat file `requirements.txt` sesuai TRD Bagian 3.2.4
- [ ] **1.8** Buat file `modules/__init__.py` (boleh kosong)
- [ ] **1.9** Siapkan file dataset (`data/dataset.xlsx`) dengan kolom minimal: `judul`, `abstrak`
  - Kolom opsional: `mahasiswa`, `tahun`, `prodi`
- [ ] **1.10** Buat file `README.md` sederhana (judul proyek, deskripsi singkat)

### ✅ Checklist Sebelum Lanjut ke Fase 2

> **WAJIB:** Semua item di bawah harus terpenuhi sebelum melanjutkan.

- [ ] Folder proyek dan semua subfolder sudah dibuat
- [ ] Virtual environment aktif dan Python 3.10/3.11 terverifikasi
- [ ] `torch.cuda.is_available()` mengembalikan `True`
- [ ] Semua library di `requirements.txt` berhasil terinstall tanpa error
- [ ] File `dataset.xlsx` tersedia di `data/` dan memiliki kolom `judul` serta `abstrak`
- [ ] File `modules/__init__.py` sudah ada

---

## Fase 2 — Backend Core (Preprocessing + Embedding + Database)

**Tujuan:** Implementasi tiga modul inti yang menangani pembersihan teks, pembuatan embedding vektor, dan penyimpanan/query ke database vektor.

**Referensi TRD:** Bagian 5.1, 5.2, 5.3

### Langkah-langkah

#### 2A — Preprocessor (`modules/preprocessor.py`)

- [ ] **2.1** Implementasi fungsi `preprocess_text(text: str) -> str` sesuai TRD Bagian 5.1
  - Case folding (lowercase)
  - Hapus karakter non-alfanumerik (kecuali spasi)
  - Normalisasi spasi ganda
  - Trim whitespace
- [ ] **2.2** Implementasi fungsi `combine_title_abstract(title: str, abstract: str) -> str`
- [ ] **2.3** Uji manual `preprocess_text()` dengan beberapa contoh:
  ```python
  # Contoh: "Implementasi Machine-Learning!!!" → "implementasi machine learning"
  ```

#### 2B — Embedder (`modules/embedder.py`)

- [ ] **2.4** Implementasi class `Embedder` sesuai TRD Bagian 5.2
- [ ] **2.5** Implementasi method `embed(text: str) -> list[float]`
- [ ] **2.6** Implementasi method `embed_batch(texts: list[str], batch_size: int = 32) -> list`
- [ ] **2.7** Uji bahwa model berhasil di-load dan menggunakan GPU:
  ```python
  embedder = Embedder()
  # Harus mencetak: [Embedder] Menggunakan device: cuda
  ```
- [ ] **2.8** Uji generate embedding dan verifikasi dimensi output = 1024:
  ```python
  vec = embedder.embed("test kalimat bahasa indonesia")
  print(len(vec))  # → 1024
  ```

#### 2C — Database (`modules/database.py`)

- [ ] **2.9** Implementasi class `VectorDatabase` sesuai TRD Bagian 5.3
- [ ] **2.10** Implementasi method `insert()`, `insert_batch()`, `query()`, `count()`
- [ ] **2.11** Uji insert satu dokumen dummy dan query kembali:
  ```python
  db = VectorDatabase()
  db.insert('test_001', [0.1]*1024, {'judul': 'test'})
  print(db.count())  # → 1
  ```
- [ ] **2.12** Bersihkan data dummy setelah pengujian (hapus folder `chroma_db/` lalu buat ulang)

### ✅ Checklist Sebelum Lanjut ke Fase 3

> **WAJIB:** Semua item di bawah harus terpenuhi sebelum melanjutkan.

- [ ] `preprocessor.py` → `preprocess_text()` menghasilkan output bersih dan konsisten
- [ ] `preprocessor.py` → `combine_title_abstract()` menggabungkan judul+abstrak dengan benar
- [ ] `embedder.py` → Model bge-m3 berhasil di-load di GPU (device: cuda)
- [ ] `embedder.py` → `embed()` menghasilkan vektor berdimensi 1024
- [ ] `embedder.py` → `embed_batch()` berfungsi untuk list of string
- [ ] `database.py` → Insert dan query ke Chroma berfungsi tanpa error
- [ ] `database.py` → Data tersimpan secara persistent (restart program, data masih ada)
- [ ] Tidak ada error import antar modul (`from modules.preprocessor import ...` dst.)

---

## Fase 3 — Logic Layer (Indexer + Searcher)

**Tujuan:** Implementasi modul indexer untuk membangun database dari dataset, dan modul searcher untuk logika pencarian kemiripan.

**Referensi TRD:** Bagian 5.4, 5.5, dan Bagian 2.2 (Alur Data)

### Langkah-langkah

#### 3A — Indexer (`modules/indexer.py`)

- [ ] **3.1** Implementasi fungsi `build_index(dataset_path: str)` sesuai TRD Bagian 5.4
  - Baca dataset Excel
  - Iterasi setiap baris: gabungkan judul+abstrak → preprocess → embed
  - Simpan batch ke Chroma
- [ ] **3.2** Jalankan indexer terhadap `data/dataset.xlsx`:
  ```bash
  python modules/indexer.py
  ```
- [ ] **3.3** Verifikasi jumlah dokumen di database sesuai jumlah baris di dataset:
  ```python
  db = VectorDatabase()
  print(db.count())  # → sesuai jumlah baris dataset
  ```
- [ ] **3.4** Catat waktu proses indexing (untuk referensi performa)

#### 3B — Searcher (`modules/searcher.py`)

- [ ] **3.5** Implementasi class `Searcher` sesuai TRD Bagian 5.5
- [ ] **3.6** Implementasi method `search(input_title: str, top_n: int = 10) -> list[dict]`
  - Preprocess input → embed → query Chroma → konversi distance ke similarity → sort
- [ ] **3.7** Uji pencarian dengan judul yang ada di dataset (harus muncul di Top-1 dengan similarity tinggi):
  ```python
  searcher = Searcher()
  results = searcher.search("judul yang sudah ada di dataset")
  print(results[0])
  ```
- [ ] **3.8** Uji pencarian dengan judul baru yang mirip topiknya
- [ ] **3.9** Uji pencarian dengan judul yang sangat berbeda (similarity harus rendah)

### ✅ Checklist Sebelum Lanjut ke Fase 4

> **WAJIB:** Semua item di bawah harus terpenuhi sebelum melanjutkan.

- [ ] Seluruh dataset berhasil di-index ke Chroma tanpa error
- [ ] `db.count()` mengembalikan jumlah yang sesuai dengan jumlah baris dataset
- [ ] `Searcher.search()` mengembalikan list of dict dengan field: `judul`, `mahasiswa`, `tahun`, `prodi`, `similarity`
- [ ] Similarity score berada di rentang 0.0 – 1.0
- [ ] Judul identik menghasilkan similarity mendekati 1.0
- [ ] Judul berbeda topik menghasilkan similarity rendah
- [ ] Hasil terurut dari similarity tertinggi ke terendah

---

## Fase 4 — Frontend (Streamlit UI)

**Tujuan:** Implementasi antarmuka web menggunakan Streamlit agar dosen dapat melakukan pencarian kemiripan judul secara interaktif.

**Referensi TRD:** Bagian 5.6

### Langkah-langkah

- [ ] **4.1** Implementasi `app.py` sesuai TRD Bagian 5.6
  - Konfigurasi halaman (`st.set_page_config`)
  - Header dan deskripsi
  - Form input judul (`st.text_input`)
  - Slider jumlah hasil (`st.slider`)
  - Tombol cari (`st.button`)
- [ ] **4.2** Integrasi dengan `Searcher` menggunakan `@st.cache_resource`
- [ ] **4.3** Implementasi tampilan hasil sebagai DataFrame dengan gradient warna pada kolom Similarity
- [ ] **4.4** Jalankan aplikasi:
  ```bash
  streamlit run app.py
  ```
- [ ] **4.5** Uji input judul kosong → harus muncul warning
- [ ] **4.6** Uji input judul valid → harus tampil tabel hasil
- [ ] **4.7** Uji slider Top-N → jumlah baris hasil harus berubah sesuai slider
- [ ] **4.8** Verifikasi tampilan responsif dan gradient warna pada kolom Similarity bekerja

### ✅ Checklist Sebelum Lanjut ke Fase 5

> **WAJIB:** Semua item di bawah harus terpenuhi sebelum melanjutkan.

- [ ] `streamlit run app.py` berjalan tanpa error
- [ ] Halaman web terbuka di browser (`http://localhost:8501`)
- [ ] Input judul kosong memunculkan pesan warning
- [ ] Input judul valid menampilkan tabel hasil dengan kolom: Judul, Mahasiswa, Tahun, Prodi, Similarity
- [ ] Slider Top-N berfungsi mengubah jumlah hasil
- [ ] Tampilan tabel menggunakan gradient warna pada kolom Similarity
- [ ] Loading spinner muncul saat proses pencarian berlangsung

---

## Fase 5 — Integrasi, Testing & Finalisasi

**Tujuan:** Memastikan seluruh komponen bekerja dengan benar secara end-to-end, menangani edge case, dan menyiapkan dokumentasi akhir.

**Referensi TRD:** Bagian 8, 9, dan 10

### Langkah-langkah

#### 5A — Testing End-to-End

- [ ] **5.1** Restart seluruh sistem dari nol (matikan Streamlit, jalankan ulang) → pastikan data persistent
- [ ] **5.2** Uji dengan minimal 5 judul berbeda, catat hasil similarity
- [ ] **5.3** Uji edge case:
  - Input dengan karakter spesial (`!!!@@@###`)
  - Input sangat pendek (1-2 kata)
  - Input sangat panjang (>200 kata)
  - Input campuran bahasa Indonesia dan Inggris

#### 5B — Incremental Update

- [ ] **5.4** Implementasi dan uji proses menambah dokumen baru tanpa rebuild index (lihat TRD Bagian 8.2)
- [ ] **5.5** Verifikasi dokumen baru muncul di hasil pencarian setelah ditambahkan

#### 5C — Finalisasi

- [ ] **5.6** Tambahkan disclaimer di UI bahwa sistem ini bukan plagiarism checker (lihat TRD Bagian 9)
- [ ] **5.7** Perbarui `README.md` dengan instruksi lengkap cara menjalankan sistem
- [ ] **5.8** Pastikan `requirements.txt` final dan sesuai dengan semua library yang terinstall
- [ ] **5.9** Review ulang semua catatan di [`REVISION_NOTES.md`](REVISION_NOTES.md) dan tindak lanjuti yang perlu

### ✅ Checklist Final

> **WAJIB:** Semua item di bawah harus terpenuhi untuk menandakan proyek selesai.

- [ ] Semua 5 fase selesai dan checklist masing-masing terpenuhi
- [ ] Sistem berjalan end-to-end tanpa error
- [ ] Data persistent setelah restart
- [ ] Incremental update berfungsi
- [ ] `README.md` lengkap dengan instruksi
- [ ] `requirements.txt` final
- [ ] Semua catatan di `REVISION_NOTES.md` sudah ditindaklanjuti atau didokumentasikan

---

## Catatan Penting

1. **Jangan loncat fase** — setiap fase membangun fondasi untuk fase berikutnya
2. **Jika menemukan masalah**, catat di [`REVISION_NOTES.md`](REVISION_NOTES.md) dengan kategori dan prioritas
3. **Jika ada perubahan dari TRD**, catat juga di `REVISION_NOTES.md` sebagai keputusan desain
4. **Backup folder `chroma_db/`** setelah indexing berhasil, agar tidak perlu index ulang jika terjadi masalah

---

*Dokumen ini dibuat berdasarkan TRD-SKTA-2025 versi 1.0*
*Terakhir diperbarui: 2025-03-03*
