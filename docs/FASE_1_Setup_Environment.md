# 🔧 FASE 1 — Setup Environment & Struktur Proyek

---

| Field | Detail |
|-------|--------|
| **Fase** | 1 dari 5 |
| **Status** | ⬜ Belum Dimulai |
| **Prasyarat** | Tidak ada (fase pertama) |
| **Fase Selanjutnya** | [Fase 2 — Backend Core](FASE_2_Backend_Core.md) |
| **Referensi TRD** | Bagian 3 (Setup Environment), Bagian 4.1 (Struktur Direktori) |

> **Tujuan:** Menyiapkan seluruh lingkungan kerja — dari instalasi software, virtual environment, dependensi Python, hingga struktur folder proyek — agar siap untuk implementasi kode di fase berikutnya.

---

## Navigasi

[← PLANNING](PLANNING.md) · **Fase 1** · [Fase 2 →](FASE_2_Backend_Core.md) · [Fase 3](FASE_3_Logic_Layer.md) · [Fase 4](FASE_4_Frontend.md) · [Fase 5](FASE_5_Integrasi_Testing.md) · [Catatan Revisi](REVISION_NOTES.md)

---

## Daftar Isi Fase 1

1. [Spesifikasi Hardware & Software](#1-spesifikasi-hardware--software)
2. [Membuat Struktur Folder Proyek](#2-membuat-struktur-folder-proyek)
3. [Setup Virtual Environment](#3-setup-virtual-environment)
4. [Instalasi CUDA Toolkit](#4-instalasi-cuda-toolkit)
5. [Instalasi Python Libraries](#5-instalasi-python-libraries)
6. [Persiapan Dataset](#6-persiapan-dataset)
7. [Pembuatan File Pendukung](#7-pembuatan-file-pendukung)
8. [Checklist Gate — Sebelum Lanjut ke Fase 2](#8-checklist-gate--sebelum-lanjut-ke-fase-2)

---

## 1. Spesifikasi Hardware & Software

Sebelum mulai, pastikan perangkat memenuhi spesifikasi minimum berikut:

| Komponen | Minimum | Disarankan |
|----------|---------|------------|
| **OS** | Windows 10 64-bit | Windows 11 64-bit |
| **Python** | 3.10 | 3.11 |
| **GPU** | NVIDIA GTX/RTX (CUDA-compatible) | NVIDIA RTX 3060+ |
| **VRAM** | 6 GB | 8 GB+ |
| **RAM** | 16 GB | 32 GB |
| **Storage Kosong** | 10 GB | 15 GB |
| **Koneksi Internet** | Diperlukan (download model ~2.5 GB) | — |

### Cara Verifikasi

```powershell
# Cek versi Python
python --version
# Output yang diharapkan: Python 3.10.x atau Python 3.11.x

# Cek GPU NVIDIA terdeteksi
nvidia-smi
# Harus menampilkan tabel dengan nama GPU, VRAM, dan driver version
```

> **⚠️ Jika Python belum terinstall:** Download dari https://www.python.org/downloads/ — pilih versi 3.10 atau 3.11. Saat instalasi, **centang "Add Python to PATH"**.

> **⚠️ Jika `nvidia-smi` tidak ditemukan:** Install NVIDIA Driver terbaru dari https://www.nvidia.com/Download/index.aspx

---

## 2. Membuat Struktur Folder Proyek

### 2.1 Struktur Target

Buat folder proyek dengan struktur berikut (sesuai TRD Bagian 4.1):

```
skripsi-similarity/
│
├── app.py                    # Entry point – Streamlit UI (dibuat di Fase 4)
│
├── modules/
│   ├── __init__.py           # Penanda package Python
│   ├── preprocessor.py       # Preprocessing teks (dibuat di Fase 2)
│   ├── embedder.py           # Wrapper model bge-m3 (dibuat di Fase 2)
│   ├── database.py           # Interaksi Chroma DB (dibuat di Fase 2)
│   ├── searcher.py           # Logika pencarian & ranking (dibuat di Fase 3)
│   └── indexer.py            # Inisialisasi & indexing dataset (dibuat di Fase 3)
│
├── data/
│   └── dataset.xlsx          # Dataset judul + abstrak (disiapkan di Fase 1)
│
├── chroma_db/                # Folder penyimpanan Chroma (auto-generated saat Fase 3)
│
├── requirements.txt          # Daftar dependensi Python
└── README.md                 # Dokumentasi proyek
```

### 2.2 Perintah untuk Membuat Folder

```powershell
# Pindah ke lokasi kerja yang diinginkan
cd D:\.KULIAHKU\Bismillah

# Buat folder utama dan subfolder
mkdir skripsi-similarity
cd skripsi-similarity
mkdir modules
mkdir data
mkdir chroma_db
```

### 2.3 Buat File Awal

Di fase ini, buat file-file berikut sebagai placeholder (isi akan diimplementasi di fase selanjutnya):

```powershell
# Buat file __init__.py (kosong — penanda package Python)
New-Item -Path modules\__init__.py -ItemType File

# Buat placeholder untuk file utama
New-Item -Path app.py -ItemType File
New-Item -Path modules\preprocessor.py -ItemType File
New-Item -Path modules\embedder.py -ItemType File
New-Item -Path modules\database.py -ItemType File
New-Item -Path modules\searcher.py -ItemType File
New-Item -Path modules\indexer.py -ItemType File
```

### Langkah — Checklist

- [ ] **1.1** Folder `skripsi-similarity/` sudah dibuat
- [ ] **1.2** Subfolder `modules/`, `data/`, `chroma_db/` sudah dibuat
- [ ] **1.3** File `modules/__init__.py` sudah ada (bisa kosong)
- [ ] **1.4** File placeholder untuk semua modul sudah dibuat

---

## 3. Setup Virtual Environment

Virtual environment memisahkan dependensi proyek ini dari Python global, mencegah konflik versi library.

### 3.1 Membuat Virtual Environment

```powershell
# Pastikan berada di folder proyek
cd D:\.KULIAHKU\Bismillah\skripsi-similarity

# Buat virtual environment bernama "venv"
python -m venv venv
```

### 3.2 Mengaktifkan Virtual Environment

```powershell
# Aktivasi di PowerShell
.\venv\Scripts\Activate.ps1

# Atau di Command Prompt (cmd)
venv\Scripts\activate.bat
```

> **💡 Tanda venv aktif:** Prompt terminal berubah menjadi `(venv) PS D:\...>` atau `(venv) D:\...>`

### 3.3 Verifikasi

```powershell
# Pastikan Python dari venv yang digunakan
python --version
# → Python 3.10.x atau 3.11.x

# Pastikan pip tersedia dan up-to-date
python -m pip install --upgrade pip
```

### 3.4 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Jalankan: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `python` tidak dikenali | Pastikan Python sudah di PATH. Atau gunakan path lengkap: `C:\Python311\python.exe` |
| Salah versi Python | Gunakan `py -3.11 -m venv venv` untuk spesifik versi |

### Langkah — Checklist

- [ ] **1.5** Virtual environment `venv/` berhasil dibuat
- [ ] **1.6** Virtual environment berhasil diaktivasi (ada prefix `(venv)` di terminal)
- [ ] **1.7** `python --version` menampilkan 3.10.x atau 3.11.x di dalam venv

---

## 4. Instalasi CUDA Toolkit

CUDA diperlukan agar PyTorch dan model bge-m3 dapat memanfaatkan GPU NVIDIA untuk komputasi.

### 4.1 Cek Kompatibilitas

```powershell
# Cek versi driver NVIDIA dan CUDA yang didukung
nvidia-smi
```

Di output `nvidia-smi`, perhatikan kolom **CUDA Version** di pojok kanan atas — ini adalah versi CUDA **maksimum** yang didukung driver Anda.

### 4.2 Download & Install

1. Buka: https://developer.nvidia.com/cuda-downloads
2. Pilih: **Windows** → **x86_64** → **10/11** → **exe (local)**
3. Download dan jalankan installer
4. Pilih **Express Installation** (rekomendasi)

> **Versi yang disarankan:** CUDA 11.8 atau CUDA 12.1 — pilih sesuai yang didukung driver Anda.

### 4.3 Verifikasi Instalasi

```powershell
# Cek nvidia-smi (driver + GPU info)
nvidia-smi

# Cek nvcc (CUDA compiler)
nvcc --version
# Output contoh: Cuda compilation tools, release 11.8, V11.8.89
```

### 4.4 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `nvcc` tidak ditemukan | Tambahkan `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin` ke PATH |
| CUDA version mismatch | Pastikan versi CUDA Toolkit ≤ versi yang ditampilkan `nvidia-smi` |
| GPU tidak terdeteksi | Update NVIDIA Driver ke versi terbaru |

### Langkah — Checklist

- [ ] **1.8** `nvidia-smi` berjalan dan menampilkan info GPU
- [ ] **1.9** `nvcc --version` menampilkan versi CUDA yang terinstall

---

## 5. Instalasi Python Libraries

### 5.1 Install PyTorch dengan CUDA Support

PyTorch harus diinstall **terlebih dahulu** dengan versi CUDA yang sesuai.

```powershell
# Untuk CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# ATAU untuk CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

> **⚠️ Pilih salah satu** sesuai versi CUDA yang terinstall di langkah 4.

### 5.2 Verifikasi PyTorch + GPU

```python
# Jalankan di Python interpreter
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Output yang diharapkan:**
```
CUDA available: True
GPU: NVIDIA GeForce RTX xxxx
```

> **⚠️ Jika `CUDA available: False`:** Kemungkinan versi CUDA PyTorch tidak cocok dengan driver. Uninstall PyTorch (`pip uninstall torch torchvision torchaudio`) dan install ulang dengan versi CUDA yang benar.

### 5.3 Install Library Utama

```powershell
# Sentence Transformers — wrapper untuk model embedding
pip install sentence-transformers

# ChromaDB — vector database
pip install chromadb

# Streamlit — web UI framework
pip install streamlit

# Pandas + Openpyxl — baca file Excel
pip install pandas openpyxl

# NumPy — operasi numerik
pip install numpy
```

### 5.4 Penjelasan Setiap Library

| Library | Versi Minimum | Fungsi dalam Proyek |
|---------|--------------|---------------------|
| `torch` | ≥ 2.0.0 | Backend komputasi untuk model embedding, CUDA support |
| `sentence-transformers` | ≥ 2.5.0 | High-level API untuk load model bge-m3 dan generate embedding |
| `chromadb` | ≥ 0.4.0 | Vector database untuk menyimpan dan query embedding |
| `streamlit` | ≥ 1.30.0 | Framework web UI untuk antarmuka pengguna |
| `pandas` | ≥ 2.0.0 | Membaca dan manipulasi dataset (xlsx/csv) |
| `openpyxl` | ≥ 3.1.0 | Engine untuk membaca file `.xlsx` (dibutuhkan oleh pandas) |
| `numpy` | ≥ 1.24.0 | Operasi array/vektor numerik |

### 5.5 Buat File `requirements.txt`

Buat file `requirements.txt` di root folder proyek dengan isi:

```
torch>=2.0.0
sentence-transformers>=2.5.0
chromadb>=0.4.0
streamlit>=1.30.0
pandas>=2.0.0
openpyxl>=3.1.0
numpy>=1.24.0
```

### 5.6 Verifikasi Semua Library

```powershell
# Cek semua library terinstall
pip list | Select-String "torch|sentence-transformers|chromadb|streamlit|pandas|openpyxl|numpy"
```

Atau verifikasi dengan import test:

```python
python -c "
import torch
import sentence_transformers
import chromadb
import streamlit
import pandas
import openpyxl
import numpy
print('Semua library berhasil diimport!')
print(f'  torch: {torch.__version__}')
print(f'  sentence-transformers: {sentence_transformers.__version__}')
print(f'  chromadb: {chromadb.__version__}')
print(f'  streamlit: {streamlit.__version__}')
print(f'  pandas: {pandas.__version__}')
print(f'  numpy: {numpy.__version__}')
"
```

### Langkah — Checklist

- [ ] **1.10** PyTorch terinstall dengan CUDA support
- [ ] **1.11** `torch.cuda.is_available()` mengembalikan `True`
- [ ] **1.12** Semua 7 library berhasil diinstall (tidak ada error saat import)
- [ ] **1.13** File `requirements.txt` sudah dibuat di root proyek

---

## 6. Persiapan Dataset

### 6.1 Format File

Dataset disimpan sebagai `data/dataset.xlsx` dengan format kolom:

| Nama Kolom | Tipe | Wajib? | Keterangan | Contoh |
|------------|------|--------|------------|--------|
| `judul` | string | **Ya** | Judul tugas akhir lengkap | Implementasi Deep Learning untuk Klasifikasi Citra |
| `abstrak` | string | **Ya** | Abstrak/ringkasan penelitian | Penelitian ini bertujuan untuk... |
| `mahasiswa` | string | Tidak | Nama penulis | Budi Santoso |
| `tahun` | string/int | Tidak | Tahun tugas akhir | 2022 |
| `prodi` | string | Tidak | Program studi | Teknik Informatika |

### 6.2 Aturan Dataset

1. **Kolom `judul` tidak boleh kosong** — ini adalah data utama
2. **Kolom `abstrak` sangat disarankan terisi** — abstrak kosong akan menurunkan kualitas embedding (lihat TRD Bagian 9)
3. Nama kolom harus **lowercase** dan persis seperti tabel di atas
4. Baris dengan `judul` kosong sebaiknya dihapus sebelum indexing
5. Tidak ada batasan jumlah baris, tapi sistem dioptimalkan untuk ±600 dokumen

### 6.3 Contoh Isi Dataset

| judul | abstrak | mahasiswa | tahun | prodi |
|-------|---------|-----------|-------|-------|
| Implementasi Deep Learning untuk Klasifikasi Citra Medis | Penelitian ini mengembangkan model deep learning berbasis CNN untuk klasifikasi citra X-ray... | Budi Santoso | 2022 | Teknik Informatika |
| Analisis Sentimen Media Sosial Menggunakan BERT | Analisis sentimen dilakukan pada data Twitter berbahasa Indonesia menggunakan model BERT... | Siti Aminah | 2023 | Sistem Informasi |

### 6.4 Validasi Dataset (Opsional)

Jalankan script kecil untuk memvalidasi dataset:

```python
import pandas as pd

df = pd.read_excel('./data/dataset.xlsx')
print(f'Jumlah baris: {len(df)}')
print(f'Kolom: {list(df.columns)}')
print(f'Judul kosong: {df["judul"].isna().sum()}')
print(f'Abstrak kosong: {df["abstrak"].isna().sum()}')
```

### Langkah — Checklist

- [ ] **1.14** File `data/dataset.xlsx` tersedia
- [ ] **1.15** Kolom `judul` dan `abstrak` ada dan terisi (minimal mayoritas baris)
- [ ] **1.16** Nama kolom sesuai format (lowercase: `judul`, `abstrak`, `mahasiswa`, `tahun`, `prodi`)

---

## 7. Pembuatan File Pendukung

### 7.1 File `README.md`

Buat file `README.md` di root proyek dengan isi minimal:

```markdown
# Sistem Deteksi Kemiripan Judul Tugas Akhir

Sistem berbasis Vector Similarity Search untuk membantu dosen memvalidasi
kemiripan topik sebelum ACC judul tugas akhir.

## Stack Teknologi
- Python 3.10/3.11
- Model: BAAI/bge-m3 (via SentenceTransformers)
- Vector DB: ChromaDB
- Frontend: Streamlit

## Cara Menjalankan
(akan dilengkapi setelah implementasi selesai)
```

### 7.2 Verifikasi Struktur Final

Setelah semua langkah di atas selesai, struktur folder harus terlihat seperti ini:

```
skripsi-similarity/
├── venv/                     ← virtual environment
├── app.py                    ← placeholder (kosong)
├── modules/
│   ├── __init__.py           ← file kosong
│   ├── preprocessor.py       ← placeholder
│   ├── embedder.py           ← placeholder
│   ├── database.py           ← placeholder
│   ├── searcher.py           ← placeholder
│   └── indexer.py            ← placeholder
├── data/
│   └── dataset.xlsx          ← dataset siap
├── chroma_db/                ← folder kosong (akan terisi di Fase 3)
├── requirements.txt          ← daftar dependensi
└── README.md                 ← dokumentasi awal
```

### Langkah — Checklist

- [ ] **1.17** File `README.md` sudah dibuat
- [ ] **1.18** Struktur folder sesuai dengan target di atas

---

## 8. Checklist Gate — Sebelum Lanjut ke Fase 2

> **🚫 JANGAN LANJUT KE FASE 2 sebelum SEMUA item di bawah tercentang.**
>
> Jika ada yang gagal, perbaiki dulu dan catat masalahnya di [REVISION_NOTES.md](REVISION_NOTES.md).

### Verifikasi Environment

- [ ] Virtual environment aktif (prefix `(venv)` di terminal)
- [ ] Python 3.10 atau 3.11 terverifikasi (`python --version`)
- [ ] CUDA terinstall dan GPU terdeteksi (`nvidia-smi` berhasil)
- [ ] `torch.cuda.is_available()` mengembalikan `True`

### Verifikasi Dependencies

- [ ] Semua 7 library terinstall tanpa error import:
  - [ ] `torch`
  - [ ] `sentence_transformers`
  - [ ] `chromadb`
  - [ ] `streamlit`
  - [ ] `pandas`
  - [ ] `openpyxl`
  - [ ] `numpy`
- [ ] File `requirements.txt` tersedia di root proyek

### Verifikasi Struktur Proyek

- [ ] Folder `modules/`, `data/`, `chroma_db/` ada
- [ ] File `modules/__init__.py` ada
- [ ] File placeholder untuk semua modul ada (meski kosong)
- [ ] File `data/dataset.xlsx` tersedia dengan kolom yang benar
- [ ] File `README.md` ada

### Verifikasi Akhir

```powershell
# Quick check — jalankan di root proyek
python -c "
import torch, sentence_transformers, chromadb, streamlit, pandas, openpyxl, numpy
import os
assert torch.cuda.is_available(), 'GPU tidak terdeteksi!'
assert os.path.exists('modules/__init__.py'), '__init__.py tidak ada!'
assert os.path.exists('data/dataset.xlsx'), 'dataset.xlsx tidak ada!'
assert os.path.exists('requirements.txt'), 'requirements.txt tidak ada!'
print('✅ FASE 1 SELESAI — Semua verifikasi berhasil!')
"
```

---

> **Fase 1 selesai?** Lanjut ke → [Fase 2 — Backend Core (Preprocessing + Embedding + Database)](FASE_2_Backend_Core.md)

---

*Referensi: TRD-SKTA-2025 Bagian 3 & 4*
