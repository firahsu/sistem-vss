# 🔍 FASE 3 — Logic Layer (Indexer + Searcher)

---

| Field | Detail |
|-------|--------|
| **Fase** | 3 dari 5 |
| **Status** | ⬜ Belum Dimulai |
| **Prasyarat** | [Fase 2](FASE_2_Backend_Core.md) selesai dan checklist gate terpenuhi |
| **Fase Selanjutnya** | [Fase 4 — Frontend](FASE_4_Frontend.md) |
| **Referensi TRD** | Bagian 5.4 (Indexer), 5.5 (Searcher), 2.2 (Alur Data), 7 (Matematika), 8.2 (Incremental) |

> **Tujuan:** Implementasi dua modul logika bisnis utama — **Indexer** untuk membangun database embedding dari dataset, dan **Searcher** untuk melakukan pencarian kemiripan judul. Setelah fase ini, seluruh backend sudah fungsional dan dapat diuji tanpa UI.

---

## Navigasi

[← Fase 2](FASE_2_Backend_Core.md) · [PLANNING](PLANNING.md) · **Fase 3** · [Fase 4 →](FASE_4_Frontend.md) · [Fase 5](FASE_5_Integrasi_Testing.md) · [Catatan Revisi](REVISION_NOTES.md)

---

## Daftar Isi Fase 3

1. [Gambaran Modul & Alur Data](#1-gambaran-modul--alur-data)
2. [Bagian A — Indexer (indexer.py)](#2-bagian-a--indexer-indexerpy)
3. [Bagian B — Searcher (searcher.py)](#3-bagian-b--searcher-searcherpy)
4. [Pengujian End-to-End Backend](#4-pengujian-end-to-end-backend)
5. [Checklist Gate — Sebelum Lanjut ke Fase 4](#5-checklist-gate--sebelum-lanjut-ke-fase-4)

---

## 1. Gambaran Modul & Alur Data

Fase ini mengimplementasi lapisan **Logic** yang menghubungkan modul Fase 2:

```
┌──────────────────────────────────────────────────────────────────────┐
│  FASE 3 — Dua modul yang diimplementasi                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  indexer.py (Fase A — Inisialisasi, dijalankan SATU KALI)   │    │
│  │                                                              │    │
│  │  dataset.xlsx ──▶ preprocessor ──▶ embedder ──▶ database     │    │
│  │  (600 baris)     (clean text)    (1024-dim)   (Chroma DB)   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  searcher.py (Fase B — Pencarian, dijalankan SETIAP QUERY)  │    │
│  │                                                              │    │
│  │  judul_input ──▶ preprocessor ──▶ embedder ──▶ database      │    │
│  │                  (clean text)    (1024-dim)   (query top-N)  │    │
│  │                                              ──▶ hasil sort  │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

| Modul | File | Kapan Dijalankan | Menggunakan Modul |
|-------|------|------------------|-------------------|
| Indexer | `modules/indexer.py` | Sekali saat setup awal | preprocessor, embedder, database |
| Searcher | `modules/searcher.py` | Setiap pencarian | preprocessor, embedder, database |

---

## 2. Bagian A — Indexer (`indexer.py`)

### 2.1 Tentang Modul Ini

**File:** `modules/indexer.py`

**Fungsi:** Membaca seluruh dataset dari file Excel, memproses setiap baris (gabungkan judul+abstrak → preprocess → embed), lalu menyimpan semua embedding beserta metadata ke ChromaDB secara batch.

**Kapan dijalankan:**
- **Pertama kali:** Saat setup awal sistem
- **Setelahnya:** Hanya jika ingin rebuild database dari nol (misal: dataset berubah total)
- **Untuk penambahan data:** Gunakan incremental insert, bukan rebuild (lihat TRD Bagian 8.2)

### 2.2 Alur Data Indexer (dari TRD Bagian 2.2 — Fase A)

```
┌─────────────────────────────────────────────┐
│              SUMBER DATA                    │
│    File .xlsx (judul + abstrak + metadata)  │
└─────────────────────────────────────────────┘
                      │
                      ▼  Baca setiap baris (pandas)
┌─────────────────────────────────────────────┐
│              PREPROCESSING                  │
│  combine_title_abstract(judul, abstrak)     │
│  → lowercase → hapus non-alfanumerik        │
│  → normalisasi spasi                        │
└─────────────────────────────────────────────┘
                      │
                      ▼  Setiap baris → 1 vektor
┌─────────────────────────────────────────────┐
│           EMBEDDING (bge-m3)                │
│  T_doc = judul + " " + abstrak (cleaned)    │
│  V_doc = Embedder.embed(T_doc)              │
│  Dimensi: 1024 float32                      │
└─────────────────────────────────────────────┘
                      │
                      ▼  Simpan batch ke Chroma
┌─────────────────────────────────────────────┐
│          CHROMA VECTOR DB                   │
│  ID: doc_0, doc_1, ..., doc_N               │
│  Embedding: V_doc (1024-dim)                │
│  Metadata: judul, mahasiswa, tahun, prodi   │
└─────────────────────────────────────────────┘
```

### 2.3 Spesifikasi Fungsi

#### Fungsi: `build_index(dataset_path: str = './data/dataset.xlsx')`

| Aspek | Detail |
|-------|--------|
| **Input** | Path ke file dataset (Excel .xlsx) |
| **Output** | Tidak ada return value — data tersimpan di ChromaDB |
| **Kolom yang dibaca** | `judul` (wajib), `abstrak` (wajib), `mahasiswa`, `tahun`, `prodi` (opsional) |
| **ID Format** | `doc_0`, `doc_1`, ..., `doc_{N-1}` (N = jumlah baris) |
| **Metode embed** | Per-dokumen satu-satu (`embed()`) — silakan optimasi ke `embed_batch()` jika perlu |
| **Simpan ke DB** | Batch sekaligus setelah semua embedding selesai |

### 2.4 Kode Implementasi

```python
# modules/indexer.py

import pandas as pd
from modules.preprocessor import combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase

def build_index(dataset_path: str = './data/dataset.xlsx'):
    """
    Membaca dataset dan membangun index embedding di Chroma.
    Jalankan satu kali saat pertama setup.
    """
    # 1. Baca dataset
    df = pd.read_excel(dataset_path)
    # Pastikan kolom: 'judul', 'abstrak', 'mahasiswa', 'tahun', 'prodi'

    # 2. Inisialisasi komponen
    embedder = Embedder()
    db = VectorDatabase()

    print(f'[Indexer] Memproses {len(df)} dokumen...')

    # 3. Proses per dokumen
    doc_ids, embeddings, metadatas = [], [], []

    for idx, row in df.iterrows():
        # Gabungkan judul + abstrak, lalu preprocess
        combined_text = combine_title_abstract(
            str(row['judul']),
            str(row['abstrak'])
        )

        # Generate embedding
        embedding = embedder.embed(combined_text)

        # Metadata yang disimpan
        doc_ids.append(f'doc_{idx}')
        embeddings.append(embedding)
        metadatas.append({
            'judul'     : str(row['judul']),
            'mahasiswa' : str(row.get('mahasiswa', '-')),
            'tahun'     : str(row.get('tahun', '-')),
            'prodi'     : str(row.get('prodi', '-'))
        })

    # 4. Simpan ke Chroma (batch)
    db.insert_batch(doc_ids, embeddings, metadatas)
    print(f'[Indexer] Selesai. Total dokumen: {db.count()}')


if __name__ == '__main__':
    build_index()
```

### 2.5 Cara Menjalankan

```powershell
# Pastikan berada di root proyek dan venv aktif
cd D:\.KULIAHKU\Bismillah\skripsi-similarity

# Jalankan indexer
python -m modules.indexer

# ATAU
python modules/indexer.py
```

> **⏱️ Estimasi waktu:**
> - GPU RTX 3060+: ~2-5 menit untuk 600 dokumen
> - CPU only: ~15-30 menit untuk 600 dokumen

### 2.6 Verifikasi Indexing

```python
# Setelah indexing selesai, verifikasi jumlah dokumen
python -c "
from modules.database import VectorDatabase
db = VectorDatabase()
print(f'Total dokumen di database: {db.count()}')
"
```

**Output yang diharapkan:** Jumlah yang sama dengan jumlah baris di `dataset.xlsx`.

### 2.7 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `FileNotFoundError: dataset.xlsx` | Pastikan file ada di `data/dataset.xlsx` |
| `KeyError: 'judul'` | Cek nama kolom di Excel — harus lowercase `judul`, bukan `Judul` |
| `KeyError: 'abstrak'` | Cek nama kolom — harus `abstrak`, bukan `Abstrak` atau `abstract` |
| Proses sangat lambat | Pastikan GPU aktif; atau optimasi dengan `embed_batch()` |
| `OutOfMemoryError` | Terlalu banyak embedding di memory — simpan per batch (misal per 100 dokumen) |
| Indexing terhenti di tengah | Hapus folder `chroma_db/` dan jalankan ulang dari awal |

### 2.8 Tips Optimasi (Opsional)

Jika indexing lambat, Anda bisa mengganti proses per-dokumen menjadi batch:

```python
# Optimasi: gunakan embed_batch() untuk efisiensi
# Setelah loop selesai mengumpulkan combined_texts:

combined_texts = []
for idx, row in df.iterrows():
    combined_text = combine_title_abstract(str(row['judul']), str(row['abstrak']))
    combined_texts.append(combined_text)
    # ... kumpulkan metadata seperti biasa

# Embed semua sekaligus
embeddings = embedder.embed_batch(combined_texts, batch_size=32)
```

### Langkah — Checklist Bagian A

- [ ] **3.1** File `modules/indexer.py` diimplementasi sesuai kode di atas
- [ ] **3.2** Indexer berhasil dijalankan tanpa error: `python -m modules.indexer`
- [ ] **3.3** `db.count()` mengembalikan jumlah yang sesuai dengan baris dataset
- [ ] **3.4** Folder `chroma_db/` terisi (bukan kosong)
- [ ] **3.5** Catat waktu proses indexing: ______ menit (isi manual)

---

## 3. Bagian B — Searcher (`searcher.py`)

### 3.1 Tentang Modul Ini

**File:** `modules/searcher.py`

**Fungsi:** Menerima judul input dari pengguna, memproses menjadi embedding, melakukan pencarian di ChromaDB, mengkonversi distance menjadi similarity score, dan mengembalikan daftar hasil terurut.

**Ini adalah modul yang langsung digunakan oleh UI (Streamlit) di Fase 4.**

### 3.2 Alur Data Searcher (dari TRD Bagian 2.2 — Fase B)

```
┌─────────────────────────────────────────────┐
│              INPUT DOSEN                    │
│     Judul yang akan divalidasi              │
│     (contoh: "machine learning citra")      │
└─────────────────────────────────────────────┘
                      │
                      ▼  Step 1: Preprocessing
┌─────────────────────────────────────────────┐
│          PREPROCESSING INPUT                │
│  preprocess_text(input_title)               │
│  → "machine learning citra"                 │
└─────────────────────────────────────────────┘
                      │
                      ▼  Step 2: Generate embedding
┌─────────────────────────────────────────────┐
│           EMBEDDING QUERY                   │
│  V_input = embedder.embed(clean_input)      │
│  V_input ∈ ℝ^1024, ‖V_input‖ = 1           │
└─────────────────────────────────────────────┘
                      │
                      ▼  Step 3: Query ke Chroma
┌─────────────────────────────────────────────┐
│          CHROMA DB QUERY                    │
│  raw_results = db.query(V_input, top_n)     │
│  Return: ids, distances, metadatas          │
└─────────────────────────────────────────────┘
                      │
                      ▼  Step 4: Konversi & Sort
┌─────────────────────────────────────────────┐
│          PROSES HASIL                       │
│  similarity = 1 - distance (cosine)         │
│  Sort descending by similarity              │
│  Return list of dict                        │
└─────────────────────────────────────────────┘
```

### 3.3 Formula Konversi Distance → Similarity

Dari TRD Bagian 7.3:

```
Cosine Similarity:
                     A · B
  Sim(A, B) = ──────────────
               ‖A‖ × ‖B‖

Karena vektor sudah ternormalisasi (‖V‖ = 1):
  Sim(A, B) = A · B  (setara dot product)

ChromaDB mengembalikan cosine distance:
  distance = 1 - similarity

Konversi kembali:
  similarity = 1 - distance

Rentang nilai:
  0.0 = tidak mirip sama sekali
  1.0 = identik secara semantik
```

### 3.4 Spesifikasi Class & Method

#### Class: `Searcher`

**Constructor:** `__init__(self)`
- Inisialisasi `Embedder` dan `VectorDatabase`

#### Method: `search(self, input_title: str, top_n: int = 10) -> list[dict]`

| Aspek | Detail |
|-------|--------|
| **Input** | `input_title`: judul yang ingin dicek kemiripannya; `top_n`: jumlah hasil |
| **Output** | List of dict, terurut dari similarity tertinggi |
| **Langkah** | 1. Preprocess input → 2. Embed → 3. Query Chroma → 4. Konversi distance → similarity → 5. Sort descending |

**Format output per item:**

```python
{
    'judul'     : 'Implementasi Algoritma ...',   # string
    'mahasiswa' : 'Budi Santoso',                 # string
    'tahun'     : '2022',                         # string
    'prodi'     : 'Teknik Informatika',           # string
    'similarity': 0.8723                          # float, 4 desimal
}
```

### 3.5 Kode Implementasi

```python
# modules/searcher.py

from modules.preprocessor import preprocess_text
from modules.embedder import Embedder
from modules.database import VectorDatabase

class Searcher:
    def __init__(self):
        self.embedder = Embedder()
        self.db = VectorDatabase()

    def search(self, input_title: str, top_n: int = 10) -> list[dict]:
        """
        Menerima judul input, mengembalikan Top-N hasil kemiripan.

        Output: list of dict dengan keys: judul, mahasiswa, tahun, prodi, similarity
        Terurut dari similarity tertinggi ke terendah.
        """
        # 1. Preprocess judul input
        clean_input = preprocess_text(input_title)

        # 2. Generate embedding
        query_vector = self.embedder.embed(clean_input)

        # 3. Query ke Chroma
        raw_results = self.db.query(query_vector, top_n=top_n)

        # 4. Proses hasil
        results = []
        ids       = raw_results['ids'][0]
        distances = raw_results['distances'][0]
        metadatas = raw_results['metadatas'][0]

        for i in range(len(ids)):
            # Chroma cosine: distance = 1 - similarity
            # Konversi kembali ke similarity score
            similarity_score = 1 - distances[i]

            results.append({
                'judul'     : metadatas[i].get('judul', '-'),
                'mahasiswa' : metadatas[i].get('mahasiswa', '-'),
                'tahun'     : metadatas[i].get('tahun', '-'),
                'prodi'     : metadatas[i].get('prodi', '-'),
                'similarity': round(similarity_score, 4)
            })

        # 5. Urutkan dari similarity tertinggi
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results
```

### 3.6 Pengujian

> **⚠️ Prasyarat:** Indexer harus sudah dijalankan (database harus terisi).

#### Test 1: Pencarian dasar

```python
python -c "
from modules.searcher import Searcher

searcher = Searcher()
results = searcher.search('implementasi deep learning untuk klasifikasi citra', top_n=5)

print(f'Jumlah hasil: {len(results)}')
print()
for i, r in enumerate(results):
    print(f'{i+1}. [{r[\"similarity\"]:.4f}] {r[\"judul\"]}')
    print(f'   Mahasiswa: {r[\"mahasiswa\"]} | Tahun: {r[\"tahun\"]} | Prodi: {r[\"prodi\"]}')
    print()
"
```

#### Test 2: Validasi format output

```python
python -c "
from modules.searcher import Searcher

searcher = Searcher()
results = searcher.search('sistem informasi', top_n=3)

# Validasi format
assert isinstance(results, list), 'Output bukan list'
assert len(results) <= 3, 'Jumlah hasil melebihi top_n'

for r in results:
    assert 'judul' in r, 'Missing key: judul'
    assert 'mahasiswa' in r, 'Missing key: mahasiswa'
    assert 'tahun' in r, 'Missing key: tahun'
    assert 'prodi' in r, 'Missing key: prodi'
    assert 'similarity' in r, 'Missing key: similarity'
    assert 0.0 <= r['similarity'] <= 1.0, f'Similarity di luar rentang: {r[\"similarity\"]}'

# Validasi urutan (descending)
for i in range(len(results) - 1):
    assert results[i]['similarity'] >= results[i+1]['similarity'], 'Urutan tidak descending!'

print('✅ Semua validasi format PASSED!')
"
```

#### Test 3: Uji semantik

```python
python -c "
from modules.searcher import Searcher

searcher = Searcher()

# Query dengan judul yang mirip salah satu di dataset
r1 = searcher.search('machine learning untuk pengenalan wajah', top_n=1)

# Query dengan topik yang sangat berbeda
r2 = searcher.search('analisis laporan keuangan perusahaan', top_n=1)

print(f'Query mirip: similarity = {r1[0][\"similarity\"]:.4f} → {r1[0][\"judul\"]}')
print(f'Query beda:  similarity = {r2[0][\"similarity\"]:.4f} → {r2[0][\"judul\"]}')
print()

# Query yang sangat mirip seharusnya punya similarity lebih tinggi
# (tergantung konten dataset, ini hanya contoh)
print('Perhatikan: query yang relevan seharusnya punya similarity lebih tinggi.')
"
```

### 3.7 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `Searcher` sangat lambat | Pertama kali lambat karena load model — selanjutnya cepat |
| Semua similarity ≈ 0 | Cek apakah database sudah terisi (`db.count()`) |
| Similarity > 1.0 atau < 0.0 | Bug di konversi distance — cek formula `1 - distance` |
| `InvalidDimensionException` | Dimensi query vector tidak cocok — pastikan model yang sama digunakan |

### Langkah — Checklist Bagian B

- [ ] **3.6** File `modules/searcher.py` diimplementasi sesuai kode di atas
- [ ] **3.7** `search()` mengembalikan list of dict dengan format yang benar
- [ ] **3.8** Similarity score berada di rentang 0.0 – 1.0
- [ ] **3.9** Hasil terurut dari similarity tertinggi ke terendah
- [ ] **3.10** Judul mirip menghasilkan similarity tinggi
- [ ] **3.11** Judul berbeda topik menghasilkan similarity rendah

---

## 4. Pengujian End-to-End Backend

Setelah Indexer dan Searcher selesai, uji keseluruhan alur backend:

```python
python -c "
from modules.searcher import Searcher
from modules.database import VectorDatabase

# Verifikasi database
db = VectorDatabase()
total = db.count()
print(f'Total dokumen di database: {total}')
assert total > 0, 'Database kosong! Jalankan indexer dulu.'

# Uji 3 pencarian berbeda
searcher = Searcher()
queries = [
    'implementasi machine learning untuk klasifikasi',
    'rancang bangun sistem informasi berbasis web',
    'analisis sentimen media sosial menggunakan NLP',
]

for q in queries:
    results = searcher.search(q, top_n=3)
    print(f'\\nQuery: \"{q}\"')
    for i, r in enumerate(results):
        print(f'  {i+1}. [{r[\"similarity\"]:.4f}] {r[\"judul\"][:60]}...')

print('\\n✅ Backend end-to-end test selesai!')
"
```

### Langkah — Checklist End-to-End

- [ ] **3.12** Database terisi dengan jumlah dokumen yang benar
- [ ] **3.13** Tiga query berbeda menghasilkan hasil yang masuk akal
- [ ] **3.14** Tidak ada error selama pengujian

---

## 5. Checklist Gate — Sebelum Lanjut ke Fase 4

> **🚫 JANGAN LANJUT KE FASE 4 sebelum SEMUA item di bawah tercentang.**
>
> Jika ada yang gagal, perbaiki dulu dan catat masalahnya di [REVISION_NOTES.md](REVISION_NOTES.md).

### Indexer

- [ ] Seluruh dataset berhasil di-index ke ChromaDB tanpa error
- [ ] `db.count()` mengembalikan jumlah yang sesuai dengan jumlah baris dataset
- [ ] Folder `chroma_db/` terisi dan tidak kosong
- [ ] Waktu indexing dicatat (untuk referensi)

### Searcher

- [ ] `Searcher.search()` mengembalikan list of dict dengan field: `judul`, `mahasiswa`, `tahun`, `prodi`, `similarity`
- [ ] Similarity score berada di rentang 0.0 – 1.0
- [ ] Judul yang identik/sangat mirip → similarity mendekati 1.0
- [ ] Judul berbeda topik → similarity rendah
- [ ] Hasil terurut dari similarity tertinggi ke terendah

### Backend End-to-End

- [ ] Alur lengkap Dataset → Index → Query → Hasil berjalan tanpa error
- [ ] Minimal 3 query berbeda diuji dan hasilnya masuk akal
- [ ] Semua modul (preprocessor, embedder, database, indexer, searcher) dapat diimport tanpa error

### Verifikasi Akhir

```powershell
python -c "
from modules.searcher import Searcher
from modules.database import VectorDatabase
db = VectorDatabase()
assert db.count() > 0, 'Database kosong!'
searcher = Searcher()
r = searcher.search('test query', top_n=1)
assert len(r) == 1 and 'similarity' in r[0], 'Format output salah!'
print(f'✅ FASE 3 SELESAI — Database: {db.count()} dokumen, Searcher berfungsi!')
"
```

---

> **Fase 3 selesai?** Lanjut ke → [Fase 4 — Frontend (Streamlit UI)](FASE_4_Frontend.md)
>
> **💡 Tips:** Backup folder `chroma_db/` sekarang! Jika terjadi masalah di fase selanjutnya, Anda tidak perlu menjalankan indexer ulang.

---

*Referensi: TRD-SKTA-2025 Bagian 2.2, 5.4, 5.5, 7, dan 8*
