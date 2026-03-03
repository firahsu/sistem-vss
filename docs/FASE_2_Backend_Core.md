# ⚙️ FASE 2 — Backend Core (Preprocessing + Embedding + Database)

---

| Field | Detail |
|-------|--------|
| **Fase** | 2 dari 5 |
| **Status** | ⬜ Belum Dimulai |
| **Prasyarat** | [Fase 1](FASE_1_Setup_Environment.md) selesai dan checklist gate terpenuhi |
| **Fase Selanjutnya** | [Fase 3 — Logic Layer](FASE_3_Logic_Layer.md) |
| **Referensi TRD** | Bagian 5.1 (Preprocessor), 5.2 (Embedder), 5.3 (Database), 6 (Skema DB) |

> **Tujuan:** Implementasi tiga modul inti sistem — preprocessing teks, pembuatan embedding vektor menggunakan model bge-m3, dan penyimpanan/query ke ChromaDB. Ketiga modul ini menjadi fondasi untuk seluruh logika bisnis di fase berikutnya.

---

## Navigasi

[← Fase 1](FASE_1_Setup_Environment.md) · [PLANNING](PLANNING.md) · **Fase 2** · [Fase 3 →](FASE_3_Logic_Layer.md) · [Fase 4](FASE_4_Frontend.md) · [Fase 5](FASE_5_Integrasi_Testing.md) · [Catatan Revisi](REVISION_NOTES.md)

---

## Daftar Isi Fase 2

1. [Gambaran Modul yang Diimplementasi](#1-gambaran-modul-yang-diimplementasi)
2. [Bagian A — Preprocessor (preprocessor.py)](#2-bagian-a--preprocessor-preprocessorpy)
3. [Bagian B — Embedder (embedder.py)](#3-bagian-b--embedder-embedderpy)
4. [Bagian C — Database (database.py)](#4-bagian-c--database-databasepy)
5. [Pengujian Integrasi Antar Modul](#5-pengujian-integrasi-antar-modul)
6. [Checklist Gate — Sebelum Lanjut ke Fase 3](#6-checklist-gate--sebelum-lanjut-ke-fase-3)

---

## 1. Gambaran Modul yang Diimplementasi

Fase ini mengimplementasi 3 modul di lapisan **Processing** dan **Storage** dari arsitektur sistem:

```
┌──────────────────────────────────────────────────────────────────┐
│  FASE 2 — Tiga modul yang diimplementasi                        │
│                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌────────────────┐ │
│  │ preprocessor.py  │──▶│  embedder.py    │──▶│  database.py   │ │
│  │                  │   │                  │   │                │ │
│  │ • preprocess_    │   │ • Embedder class │   │ • VectorDB     │ │
│  │   text()         │   │ • embed()        │   │ • insert()     │ │
│  │ • combine_title_ │   │ • embed_batch()  │   │ • query()      │ │
│  │   abstract()     │   │                  │   │ • count()      │ │
│  └─────────────────┘   └─────────────────┘   └────────────────┘ │
│       Teks bersih    →    Vektor 1024-dim   →   Simpan/Query     │
└──────────────────────────────────────────────────────────────────┘
```

| Modul | File | Input | Output |
|-------|------|-------|--------|
| Preprocessor | `modules/preprocessor.py` | String mentah | String bersih (lowercase, tanpa karakter spesial) |
| Embedder | `modules/embedder.py` | String bersih | Dense vector float32, dimensi 1024 |
| Database | `modules/database.py` | Vector + metadata | Tersimpan di ChromaDB; query mengembalikan Top-N |

---

## 2. Bagian A — Preprocessor (`preprocessor.py`)

### 2.1 Tentang Modul Ini

**File:** `modules/preprocessor.py`

**Fungsi:** Membersihkan teks agar konsisten sebelum masuk ke model embedding. Menggunakan pendekatan **light cleaning** — tidak melakukan stemming atau stopword removal karena model bge-m3 sudah mampu memahami konteks bahasa natural.

**Keputusan Desain (dari TRD Bagian 10):**
| Keputusan | Alasan |
|-----------|--------|
| Light cleaning, bukan agresif | Model bge-m3 sudah paham konteks; stemming justru merusak makna semantik |
| Tidak hapus stopword | Stopword bisa memberikan konteks penting untuk pemahaman makna |

### 2.2 Spesifikasi Fungsi

#### Fungsi 1: `preprocess_text(text: str) -> str`

| Aspek | Detail |
|-------|--------|
| **Input** | String mentah (judul, abstrak, atau gabungan) |
| **Output** | String bersih |
| **Langkah** | 1. Case folding (lowercase) → 2. Hapus karakter non-alfanumerik kecuali spasi → 3. Normalisasi spasi ganda → 4. Trim whitespace awal/akhir |

**Contoh transformasi:**

| Input | Output |
|-------|--------|
| `"Implementasi Machine-Learning!!!"` | `"implementasi machine learning"` |
| `"Analisis   Sentimen @Twitter #2023"` | `"analisis sentimen twitter 2023"` |
| `"  DEEP LEARNING untuk NLP  "` | `"deep learning untuk nlp"` |
| `"Rancang-Bangun Sistem (Berbasis Web)"` | `"rancang bangun sistem berbasis web"` |

#### Fungsi 2: `combine_title_abstract(title: str, abstract: str) -> str`

| Aspek | Detail |
|-------|--------|
| **Input** | Judul (string) dan Abstrak (string) |
| **Output** | String gabungan yang sudah di-preprocess |
| **Strategi** | Gabungkan `judul + " " + abstrak`, lalu jalankan `preprocess_text()` |

**Keputusan Desain (dari TRD Bagian 10):** Judul dan abstrak digabung karena memberikan konteks lebih kaya — satu vektor per dokumen, sederhana dan efektif.

### 2.3 Kode Implementasi

```python
# modules/preprocessor.py

import re

def preprocess_text(text: str) -> str:
    """
    Light text cleaning untuk input embedding.
    Input : string (judul atau gabungan judul+abstrak)
    Output: string bersih
    """
    # 1. Case folding
    text = text.lower()

    # 2. Hapus karakter non-alfanumerik (kecuali spasi)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # 3. Normalisasi spasi ganda
    text = re.sub(r'\s+', ' ', text)

    # 4. Trim whitespace awal/akhir
    text = text.strip()

    return text


def combine_title_abstract(title: str, abstract: str) -> str:
    """
    Menggabungkan judul dan abstrak sebelum di-embed.
    Strategi: judul + spasi + abstrak
    """
    combined = title + ' ' + abstract
    return preprocess_text(combined)
```

### 2.4 Pengujian Unit

Setelah implementasi, jalankan pengujian berikut di terminal:

```python
# Jalankan dari root proyek (skripsi-similarity/)
python -c "
from modules.preprocessor import preprocess_text, combine_title_abstract

# Test preprocess_text
assert preprocess_text('Implementasi Machine-Learning!!!') == 'implementasi machine learning'
assert preprocess_text('  DEEP LEARNING untuk NLP  ') == 'deep learning untuk nlp'
assert preprocess_text('Analisis   Sentimen @Twitter #2023') == 'analisis sentimen twitter 2023'
assert preprocess_text('') == ''

# Test combine_title_abstract
result = combine_title_abstract('Judul TA', 'Abstrak penelitian ini...')
assert result == 'judul ta abstrak penelitian ini'

print('✅ Semua test preprocessor PASSED!')
"
```

### Langkah — Checklist Bagian A

- [ ] **2.1** File `modules/preprocessor.py` diimplementasi sesuai kode di atas
- [ ] **2.2** Fungsi `preprocess_text()` berfungsi dengan benar (4 test case passed)
- [ ] **2.3** Fungsi `combine_title_abstract()` berfungsi dengan benar
- [ ] **2.4** Import berhasil: `from modules.preprocessor import preprocess_text, combine_title_abstract`

---

## 3. Bagian B — Embedder (`embedder.py`)

### 3.1 Tentang Modul Ini

**File:** `modules/embedder.py`

**Fungsi:** Mengkonversi teks menjadi dense vector menggunakan model **BAAI/bge-m3** melalui library SentenceTransformers. Vektor ini merepresentasikan makna semantik teks dalam ruang berdimensi 1024.

**Tentang Model bge-m3:**

| Aspek | Detail |
|-------|--------|
| **Nama Model** | `BAAI/bge-m3` |
| **Sumber** | HuggingFace: https://huggingface.co/BAAI/bge-m3 |
| **Ukuran Download** | ~2.5 GB (otomatis download pertama kali) |
| **Dimensi Output** | 1024 (dense vector float32) |
| **Bahasa** | Multilingual (mendukung Bahasa Indonesia) |
| **Keunggulan** | State-of-the-art untuk semantic retrieval, mendukung banyak bahasa |
| **Cache Location** | `C:\Users\<username>\.cache\huggingface\hub\` |

**Keputusan Desain (dari TRD Bagian 10):** Model bge-m3 dipilih karena kemampuan multilingual (penting untuk dataset Bahasa Indonesia) dan performa state-of-the-art untuk tugas semantic retrieval.

### 3.2 Spesifikasi Class & Method

#### Class: `Embedder`

**Constructor:** `__init__(self, model_name: str = 'BAAI/bge-m3')`
- Deteksi GPU otomatis (CUDA > CPU)
- Load model SentenceTransformer
- Print device yang digunakan

#### Method 1: `embed(self, text: str) -> list[float]`

| Aspek | Detail |
|-------|--------|
| **Input** | Satu string teks |
| **Output** | List of float, panjang 1024 |
| **Parameter penting** | `normalize_embeddings=True` — vektor ternormalisasi agar `‖V‖ = 1` |
| **Catatan** | Karena sudah ternormalisasi, cosine similarity = dot product (lebih efisien) |

#### Method 2: `embed_batch(self, texts: list[str], batch_size: int = 32) -> list`

| Aspek | Detail |
|-------|--------|
| **Input** | List of string |
| **Output** | List of list of float |
| **Batch Size** | Default 32 — optimal untuk VRAM 6-8 GB |
| **Kegunaan** | Lebih efisien untuk indexing banyak dokumen sekaligus |

### 3.3 Representasi Matematika

Dari TRD Bagian 7:

```
Untuk embedding dokumen:
  T_doc  = Judul_d + " " + Abstrak_d     # Gabungan teks
  T_proc = preprocess(T_doc)              # Light cleaning
  V_doc  = E(T_proc)                      # Dense vector via bge-m3
  Dimana: V_doc ∈ ℝ^1024, ‖V_doc‖ = 1 (ternormalisasi)

Untuk embedding query:
  T_input = Judul_input                   # Hanya judul dari user
  T_proc  = preprocess(T_input)
  V_input = E(T_proc)
  Dimana: V_input ∈ ℝ^1024, ‖V_input‖ = 1
```

### 3.4 Kode Implementasi

```python
# modules/embedder.py

from sentence_transformers import SentenceTransformer
import torch

class Embedder:
    def __init__(self, model_name: str = 'BAAI/bge-m3'):
        # Deteksi GPU secara otomatis
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f'[Embedder] Menggunakan device: {self.device}')

        # Load model (download otomatis jika belum ada)
        self.model = SentenceTransformer(model_name, device=self.device)

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding untuk satu string.
        Output: list of float (dense vector, dimensi 1024)
        """
        vector = self.model.encode(
            text,
            normalize_embeddings=True,   # penting untuk cosine similarity
            show_progress_bar=False
        )
        return vector.tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list:
        """
        Generate embedding untuk banyak teks sekaligus (lebih efisien).
        """
        vectors = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return [v.tolist() for v in vectors]
```

### 3.5 Pengujian Unit

> **⚠️ Catatan:** Test ini membutuhkan download model ~2.5 GB pada pertama kali. Pastikan koneksi internet tersedia.

```python
# Jalankan dari root proyek
python -c "
from modules.embedder import Embedder

# Test 1: Inisialisasi — harus menggunakan CUDA
embedder = Embedder()
# Output: [Embedder] Menggunakan device: cuda

# Test 2: Embed satu teks — dimensi harus 1024
vec = embedder.embed('implementasi machine learning untuk klasifikasi citra')
assert len(vec) == 1024, f'Dimensi salah: {len(vec)}'
assert isinstance(vec, list), 'Output bukan list'
assert isinstance(vec[0], float), 'Elemen bukan float'
print(f'Dimensi vektor: {len(vec)} ✓')

# Test 3: Vektor ternormalisasi (panjang ≈ 1.0)
import numpy as np
norm = np.linalg.norm(vec)
assert abs(norm - 1.0) < 0.01, f'Vektor tidak ternormalisasi: norm={norm}'
print(f'Norm vektor: {norm:.4f} ≈ 1.0 ✓')

# Test 4: Embed batch
vecs = embedder.embed_batch(['teks pertama', 'teks kedua', 'teks ketiga'])
assert len(vecs) == 3, f'Jumlah output salah: {len(vecs)}'
assert len(vecs[0]) == 1024, f'Dimensi batch salah: {len(vecs[0])}'
print(f'Batch embedding: {len(vecs)} vektor ✓')

print('\\n✅ Semua test embedder PASSED!')
"
```

### 3.6 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Download model sangat lambat | Gunakan VPN atau mirror HuggingFace |
| `OutOfMemoryError` saat embed_batch | Kurangi `batch_size` (coba 16 atau 8) |
| Model menggunakan CPU padahal GPU ada | Cek `torch.cuda.is_available()` — mungkin PyTorch tidak terinstall dengan CUDA |
| Import error `sentence_transformers` | Pastikan `pip install sentence-transformers` (dengan tanda hubung) |

### Langkah — Checklist Bagian B

- [ ] **2.5** File `modules/embedder.py` diimplementasi sesuai kode di atas
- [ ] **2.6** Model berhasil di-load dan menggunakan device `cuda`
- [ ] **2.7** `embed()` menghasilkan vektor berdimensi 1024
- [ ] **2.8** Vektor ternormalisasi (norm ≈ 1.0)
- [ ] **2.9** `embed_batch()` berfungsi untuk list of string
- [ ] **2.10** Import berhasil: `from modules.embedder import Embedder`

---

## 4. Bagian C — Database (`modules/database.py`)

### 4.1 Tentang Modul Ini

**File:** `modules/database.py`

**Fungsi:** Mengelola koneksi ke ChromaDB — menyimpan embedding beserta metadata dan melakukan query similarity search. Menggunakan **persistent storage** agar data tidak hilang saat program ditutup.

**Tentang ChromaDB:**

| Aspek | Detail |
|-------|--------|
| **Tipe** | Embedded vector database |
| **Penyimpanan** | Persistent di disk (`./chroma_db/`) |
| **Distance Metric** | Cosine distance (`hnsw:space: cosine`) |
| **Skala** | Optimal untuk dataset kecil-menengah (ratusan–ribuan dokumen) |
| **Integrasi** | Native Python, tidak perlu server terpisah |

**Keputusan Desain (dari TRD Bagian 10):** ChromaDB dipilih karena cocok untuk skala kecil-menengah, integrasi Python yang mudah, dan mendukung penyimpanan metadata.

### 4.2 Skema Collection (dari TRD Bagian 6)

| Field | Detail |
|-------|--------|
| **Nama Collection** | `skripsi_embeddings` |
| **Distance Metric** | cosine (konfigurasi via `hnsw:space`) |
| **Tipe Embedding** | Dense float32 vector |
| **Dimensi Vector** | 1024 (output default bge-m3) |
| **Storage Location** | `./chroma_db/` (persistent, di disk lokal) |

**Metadata yang disimpan per dokumen:**

| Field Metadata | Tipe | Contoh |
|----------------|------|--------|
| `judul` | string | "Implementasi Deep Learning untuk Klasifikasi Citra" |
| `mahasiswa` | string | "Budi Santoso" |
| `tahun` | string | "2022" |
| `prodi` | string | "Teknik Informatika" |

**Format ID dokumen:** `doc_0`, `doc_1`, `doc_2`, dst. (berdasarkan index baris dataset)

### 4.3 Spesifikasi Class & Method

#### Class: `VectorDatabase`

**Constructor:** `__init__(self, persist_path: str = './chroma_db')`
- Membuat `PersistentClient` — data tersimpan di folder yang ditentukan
- Membuat atau mengambil collection `skripsi_embeddings` dengan cosine distance

#### Method 1: `insert(self, doc_id: str, embedding: list, metadata: dict)`

| Aspek | Detail |
|-------|--------|
| **Fungsi** | Menyimpan satu dokumen ke collection |
| **Parameter** | `doc_id`: ID unik (string), `embedding`: vektor 1024-dim, `metadata`: dict info dokumen |
| **Catatan** | Digunakan untuk incremental update (tambah dokumen baru satu per satu) |

#### Method 2: `insert_batch(self, doc_ids: list, embeddings: list, metadatas: list)`

| Aspek | Detail |
|-------|--------|
| **Fungsi** | Menyimpan banyak dokumen sekaligus (lebih efisien) |
| **Catatan** | Digunakan saat indexing awal seluruh dataset |

#### Method 3: `query(self, query_embedding: list, top_n: int = 10) -> dict`

| Aspek | Detail |
|-------|--------|
| **Fungsi** | Mencari Top-N dokumen paling mirip berdasarkan cosine distance |
| **Output** | Dict berisi `ids`, `distances`, `metadatas` |
| **Penting** | `distances` = cosine distance = `1 - similarity` (perlu dikonversi di Searcher) |

#### Method 4: `count(self) -> int`

| Aspek | Detail |
|-------|--------|
| **Fungsi** | Mengembalikan jumlah dokumen dalam collection |

### 4.4 Kode Implementasi

```python
# modules/database.py

import chromadb

class VectorDatabase:
    def __init__(self, persist_path: str = './chroma_db'):
        # Persistent client – data tersimpan di disk
        self.client = chromadb.PersistentClient(path=persist_path)

        # Buat atau ambil collection yang sudah ada
        self.collection = self.client.get_or_create_collection(
            name='skripsi_embeddings',
            metadata={'hnsw:space': 'cosine'}   # gunakan cosine distance
        )

    def insert(self, doc_id: str, embedding: list, metadata: dict):
        """
        Menyimpan satu dokumen ke Chroma.
        metadata contoh: {'judul': '...', 'mahasiswa': '...', 'tahun': '...', 'prodi': '...'}
        """
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def insert_batch(self, doc_ids: list, embeddings: list, metadatas: list):
        """
        Menyimpan banyak dokumen sekaligus (lebih efisien).
        """
        self.collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_embedding: list, top_n: int = 10) -> dict:
        """
        Query Top-N dokumen paling mirip.
        Output: dict berisi 'ids', 'distances', 'metadatas'
        
        CATATAN: Chroma cosine distance = 1 - cosine_similarity
        Untuk mendapatkan similarity score: similarity = 1 - distance
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_n,
            include=['metadatas', 'distances']
        )
        return results

    def count(self) -> int:
        """Mengembalikan jumlah dokumen dalam database."""
        return self.collection.count()
```

### 4.5 Pengujian Unit

```python
# Jalankan dari root proyek
python -c "
import os, shutil
from modules.database import VectorDatabase

# Setup: gunakan folder test terpisah agar tidak mengganggu data asli
test_path = './chroma_db_test'
if os.path.exists(test_path):
    shutil.rmtree(test_path)

# Test 1: Inisialisasi
db = VectorDatabase(persist_path=test_path)
assert db.count() == 0, 'Database seharusnya kosong'
print(f'Database baru, count = {db.count()} ✓')

# Test 2: Insert satu dokumen (vektor dummy 1024-dim)
dummy_vec = [0.01] * 1024
db.insert('test_001', dummy_vec, {'judul': 'Judul Test 1', 'mahasiswa': 'Tester'})
assert db.count() == 1, f'Count seharusnya 1, dapat {db.count()}'
print(f'Insert 1 dokumen, count = {db.count()} ✓')

# Test 3: Insert batch
ids = ['test_002', 'test_003']
vecs = [[0.02] * 1024, [0.03] * 1024]
metas = [
    {'judul': 'Judul Test 2', 'mahasiswa': 'Tester 2'},
    {'judul': 'Judul Test 3', 'mahasiswa': 'Tester 3'}
]
db.insert_batch(ids, vecs, metas)
assert db.count() == 3, f'Count seharusnya 3, dapat {db.count()}'
print(f'Insert batch 2 dokumen, count = {db.count()} ✓')

# Test 4: Query
results = db.query(dummy_vec, top_n=2)
assert 'ids' in results, 'Hasil query tidak memiliki key ids'
assert 'distances' in results, 'Hasil query tidak memiliki key distances'
assert 'metadatas' in results, 'Hasil query tidak memiliki key metadatas'
assert len(results['ids'][0]) == 2, f'Seharusnya 2 hasil, dapat {len(results[\"ids\"][0])}'
print(f'Query top-2 berhasil, {len(results[\"ids\"][0])} hasil ✓')

# Test 5: Persistent — buat instance baru, data harus masih ada
db2 = VectorDatabase(persist_path=test_path)
assert db2.count() == 3, f'Data tidak persistent! Count = {db2.count()}'
print(f'Persistent check, count = {db2.count()} ✓')

# Cleanup
shutil.rmtree(test_path)
print('\\n✅ Semua test database PASSED!')
"
```

### 4.6 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `PermissionError` pada folder chroma_db | Tutup semua program yang membuka folder tersebut |
| `DuplicateIDError` saat insert | ID dokumen sudah ada — gunakan ID unik |
| Collection tidak ditemukan | Pastikan `persist_path` konsisten di semua pemanggilan |
| `sqlite3.OperationalError` | ChromaDB versi lama — `pip install --upgrade chromadb` |

### Langkah — Checklist Bagian C

- [ ] **2.11** File `modules/database.py` diimplementasi sesuai kode di atas
- [ ] **2.12** `insert()` berhasil menyimpan dokumen
- [ ] **2.13** `insert_batch()` berhasil menyimpan banyak dokumen
- [ ] **2.14** `query()` mengembalikan hasil dengan key `ids`, `distances`, `metadatas`
- [ ] **2.15** `count()` mengembalikan jumlah yang benar
- [ ] **2.16** Data persistent (restart program, data masih ada)
- [ ] **2.17** Import berhasil: `from modules.database import VectorDatabase`

---

## 5. Pengujian Integrasi Antar Modul

Setelah ketiga modul selesai, uji alur data end-to-end: **Teks → Preprocess → Embed → Simpan → Query**

```python
# Jalankan dari root proyek
python -c "
import os, shutil
from modules.preprocessor import preprocess_text, combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase

# Setup
test_path = './chroma_db_integration_test'
if os.path.exists(test_path):
    shutil.rmtree(test_path)

# 1. Inisialisasi
embedder = Embedder()
db = VectorDatabase(persist_path=test_path)

# 2. Simulasi proses indexing — preprocess + embed + simpan
docs = [
    ('Implementasi Deep Learning untuk Klasifikasi Citra', 'Penelitian ini menggunakan CNN untuk citra medis'),
    ('Analisis Sentimen di Media Sosial', 'Analisis sentimen Twitter menggunakan BERT'),
    ('Rancang Bangun Sistem Informasi Perpustakaan', 'Sistem informasi berbasis web untuk perpustakaan'),
]

for i, (judul, abstrak) in enumerate(docs):
    combined = combine_title_abstract(judul, abstrak)
    vec = embedder.embed(combined)
    db.insert(f'doc_{i}', vec, {'judul': judul, 'mahasiswa': f'Mahasiswa {i+1}'})

print(f'Total dokumen di DB: {db.count()}')

# 3. Simulasi query — preprocess + embed + query
query_text = preprocess_text('machine learning klasifikasi gambar')
query_vec = embedder.embed(query_text)
results = db.query(query_vec, top_n=3)

print('\\nHasil query:')
for i in range(len(results['ids'][0])):
    similarity = 1 - results['distances'][0][i]
    judul = results['metadatas'][0][i]['judul']
    print(f'  {i+1}. [{similarity:.4f}] {judul}')

# Cleanup
shutil.rmtree(test_path)
print('\\n✅ Test integrasi PASSED!')
"
```

**Output yang diharapkan:**
- Dokumen tentang "Deep Learning/Klasifikasi Citra" harus memiliki similarity tertinggi
- Dokumen tentang "Sistem Informasi Perpustakaan" harus memiliki similarity terendah

### Langkah — Checklist Integrasi

- [ ] **2.18** Alur Preprocess → Embed → Insert berjalan tanpa error
- [ ] **2.19** Alur Preprocess → Embed → Query mengembalikan hasil yang masuk akal
- [ ] **2.20** Tidak ada error import antar modul

---

## 6. Checklist Gate — Sebelum Lanjut ke Fase 3

> **🚫 JANGAN LANJUT KE FASE 3 sebelum SEMUA item di bawah tercentang.**
>
> Jika ada yang gagal, perbaiki dulu dan catat masalahnya di [REVISION_NOTES.md](REVISION_NOTES.md).

### Preprocessor

- [ ] `preprocess_text()` menghasilkan output bersih dan konsisten
- [ ] `combine_title_abstract()` menggabungkan judul+abstrak dengan benar
- [ ] Semua test case preprocessor PASSED

### Embedder

- [ ] Model bge-m3 berhasil di-load di GPU (`device: cuda`)
- [ ] `embed()` menghasilkan vektor berdimensi 1024
- [ ] Vektor ternormalisasi (norm ≈ 1.0)
- [ ] `embed_batch()` berfungsi tanpa error
- [ ] Semua test case embedder PASSED

### Database

- [ ] `insert()` dan `insert_batch()` berfungsi
- [ ] `query()` mengembalikan hasil yang benar
- [ ] `count()` konsisten
- [ ] Data persistent (tetap ada setelah restart)
- [ ] Semua test case database PASSED

### Integrasi

- [ ] Alur lengkap Preprocess → Embed → Insert → Query berjalan tanpa error
- [ ] Import antar modul tidak bermasalah
- [ ] Hasil query masuk akal secara semantik (judul mirip → similarity tinggi)

### Verifikasi Akhir

```powershell
# Quick integration check
python -c "
from modules.preprocessor import preprocess_text, combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase
print('✅ Semua modul Fase 2 dapat diimport tanpa error!')
"
```

---

> **Fase 2 selesai?** Lanjut ke → [Fase 3 — Logic Layer (Indexer + Searcher)](FASE_3_Logic_Layer.md)

---

*Referensi: TRD-SKTA-2025 Bagian 5.1, 5.2, 5.3, 6, dan 7*
