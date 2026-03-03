# TECHNICAL REQUIREMENTS DOCUMENT
### TRD-SKTA-2025

---

# Sistem Deteksi Kemiripan Judul Tugas Akhir
## Berbasis Vector Similarity Search

| Field | Detail |
|---|---|
| **Versi Dokumen** | 1.0 |
| **Status** | Draft – Panduan Implementasi |
| **Platform** | Windows 10/11 + NVIDIA RTX GPU |
| **Stack Utama** | Python · bge-m3 · ChromaDB · Streamlit |
| **Dataset** | ±600 dokumen skripsi (dinamis) |

> Dokumen ini bersifat panduan teknis internal untuk pengembang sistem.

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Arsitektur Sistem](#2-arsitektur-sistem)
3. [Setup Environment](#3-setup-environment)
4. [Struktur Modul Python](#4-struktur-modul-python)
5. [Spesifikasi Fungsi & Pseudocode](#5-spesifikasi-fungsi--pseudocode)
6. [Skema Database & Metadata Chroma](#6-skema-database--metadata-chroma)
7. [Representasi Matematika Sistem](#7-representasi-matematika-sistem)
8. [Panduan Menjalankan Sistem](#8-panduan-menjalankan-sistem)
9. [Batasan Sistem & Mitigasi Risiko](#9-batasan-sistem--mitigasi-risiko)
10. [Ringkasan Keputusan Desain](#10-ringkasan-keputusan-desain)

---

## 1. Ringkasan Eksekutif

Dokumen ini merupakan **Technical Requirements Document (TRD)** yang berfungsi sebagai panduan implementasi lengkap untuk sistem deteksi kemiripan judul tugas akhir berbasis **Vector Similarity Search**. Dokumen mencakup spesifikasi environment, struktur modul, skema database, alur data, dan contoh pseudocode yang dapat langsung dijadikan acuan coding.

| Field | Detail |
|---|---|
| **Tujuan Sistem** | Membantu dosen memvalidasi kemiripan topik sebelum ACC judul tugas akhir |
| **Pendekatan** | Semantic embedding berbasis model bge-m3 + cosine similarity |
| **Target Pengguna** | Dosen pembimbing / penguji |
| **Skala Dataset** | ±600 dokumen (dinamis, dapat bertambah) |
| **Tipe Output** | Daftar judul dengan similarity score, terurut dari tertinggi |

---

## 2. Arsitektur Sistem

### 2.1 Gambaran Lapisan Sistem

Sistem terdiri dari lima lapisan utama yang bekerja secara modular dan saling terhubung:

| No | Layer | Komponen | Fungsi Utama |
|---|---|---|---|
| 1 | User Layer | Dosen | Input judul, lihat hasil |
| 2 | Presentation Layer | Streamlit | UI web, form input, tampilan hasil |
| 3 | Processing Layer | Preprocessing + Embedding | Bersihkan teks, hasilkan vektor |
| 4 | Storage Layer | Chroma Vector DB | Simpan & query vektor embedding |
| 5 | Retrieval Layer | Cosine Similarity Engine | Hitung & ranking kemiripan |

---

### 2.2 Alur Data Sistem (Flowchart)

#### Fase A — Inisialisasi Database *(Dijalankan Satu Kali)*

Proses ini dijalankan satu kali saat pertama kali membangun basis data embedding.

```
┌─────────────────────────────────────────────┐
│              SUMBER DATA                    │
│    File .csv / .xlsx (judul + abstrak)      │
└─────────────────────────────────────────────┘
                      │
                      ▼  Baca setiap baris
┌─────────────────────────────────────────────┐
│              PREPROCESSING                  │
│  lowercase → hapus non-alfanumerik          │
│  → normalisasi spasi                        │
└─────────────────────────────────────────────┘
                      │
                      ▼  Gabungkan judul + abstrak
┌─────────────────────────────────────────────┐
│           EMBEDDING (bge-m3)                │
│  T_doc = Judul + " " + Abstrak              │
│  V_doc = E(T_doc)                           │
└─────────────────────────────────────────────┘
                      │
                      ▼  Simpan ke database
┌─────────────────────────────────────────────┐
│          CHROMA VECTOR DB                   │
│  Simpan V_doc + metadata                    │
│  (judul, mahasiswa, tahun, prodi)           │
└─────────────────────────────────────────────┘
```

---

#### Fase B — Pencarian *(Setiap Query)*

Proses ini berjalan setiap kali dosen melakukan pencarian.

```
┌─────────────────────────────────────────────┐
│              INPUT DOSEN                    │
│     Judul yang akan divalidasi              │
└─────────────────────────────────────────────┘
                      │
                      ▼  Preprocessing
┌─────────────────────────────────────────────┐
│          PREPROCESSING INPUT                │
│  lowercase → bersihkan → normalisasi spasi  │
└─────────────────────────────────────────────┘
                      │
                      ▼  Generate embedding
┌─────────────────────────────────────────────┐
│           EMBEDDING QUERY                   │
│       V_input = E(Judul_input)              │
└─────────────────────────────────────────────┘
                      │
                      ▼  Query ke Chroma
┌─────────────────────────────────────────────┐
│          COSINE SIMILARITY                  │
│  Sim(A,B) = (A·B) / (‖A‖ × ‖B‖)           │
└─────────────────────────────────────────────┘
                      │
                      ▼  Urutkan & filter Top-N
┌─────────────────────────────────────────────┐
│                OUTPUT                       │
│  Daftar judul + similarity score            │
│  (tertinggi → terendah)                     │
└─────────────────────────────────────────────┘
```

---

## 3. Setup Environment

### 3.1 Spesifikasi Hardware & OS

| Komponen | Spesifikasi |
|---|---|
| **Operating System** | Windows 10/11 (64-bit) |
| **Python Version** | Python 3.10 atau 3.11 (direkomendasikan) |
| **GPU** | NVIDIA RTX (CUDA-compatible) |
| **VRAM** | Minimum 6 GB (disarankan 8 GB+) |
| **RAM** | Minimum 16 GB |
| **Storage** | Minimum 10 GB free (untuk model bge-m3) |

---

### 3.2 Instalasi Dependencies

#### 3.2.1 Buat Virtual Environment

```bash
# Buka Command Prompt atau PowerShell
python -m venv venv

# Aktivasi virtual environment
venv\Scripts\activate
```

#### 3.2.2 Install CUDA Toolkit (untuk GPU)

Download CUDA Toolkit dari: **https://developer.nvidia.com/cuda-downloads**
(versi CUDA 11.8 atau 12.1 disarankan)

```bash
# Verifikasi instalasi CUDA
nvidia-smi
nvcc --version
```

#### 3.2.3 Install Python Libraries

```bash
# Install PyTorch dengan CUDA support (sesuaikan versi CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install library utama sistem
pip install sentence-transformers
pip install chromadb
pip install streamlit
pip install pandas openpyxl
pip install numpy
```

#### 3.2.4 File `requirements.txt`

```
torch>=2.0.0
sentence-transformers>=2.5.0
chromadb>=0.4.0
streamlit>=1.30.0
pandas>=2.0.0
openpyxl>=3.1.0
numpy>=1.24.0
```

#### 3.2.5 Download Model bge-m3

Model akan otomatis diunduh saat pertama kali digunakan oleh `sentence-transformers` (~2.5 GB). Pastikan koneksi internet tersedia.

```bash
# Model akan diunduh secara otomatis ke cache HuggingFace
# Default cache path di Windows:
# C:\Users\<username>\.cache\huggingface\hub
```

---

## 4. Struktur Modul Python

### 4.1 Struktur Direktori Proyek

```
skripsi-similarity/
│
├── app.py                    # Entry point – Streamlit UI
│
├── modules/
│   ├── __init__.py
│   ├── preprocessor.py       # Preprocessing teks
│   ├── embedder.py           # Wrapper model bge-m3
│   ├── database.py           # Interaksi Chroma DB
│   ├── searcher.py           # Logika pencarian & ranking
│   └── indexer.py            # Inisialisasi & indexing dataset
│
├── data/
│   └── dataset.xlsx          # Dataset judul + abstrak
│
├── chroma_db/                # Folder penyimpanan Chroma (auto-generated)
│
├── requirements.txt
└── README.md
```

---

### 4.2 Deskripsi Setiap Modul

| Modul | File | Tanggung Jawab |
|---|---|---|
| Preprocessor | `preprocessor.py` | Membersihkan teks: lowercase, hapus karakter, normalisasi spasi |
| Embedder | `embedder.py` | Load model bge-m3, generate dense vector dari teks |
| Database | `database.py` | Koneksi ke Chroma, simpan/query embedding + metadata |
| Searcher | `searcher.py` | Menerima input judul, query ke DB, return Top-N hasil |
| Indexer | `indexer.py` | Baca dataset, proses, simpan semua embedding ke Chroma |
| App (UI) | `app.py` | Streamlit interface: form input, tampilkan hasil similarity |

---

## 5. Spesifikasi Fungsi & Pseudocode

### 5.1 `preprocessor.py`

> **Tujuan:** Membersihkan teks agar konsisten sebelum masuk ke model embedding. Light cleaning — **TIDAK** melakukan stemming atau stopword removal.

```python
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

---

### 5.2 `embedder.py`

> **Model:** BAAI/bge-m3 via SentenceTransformers. Mendukung GPU CUDA otomatis. Output: dense vector float32.

```python
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
        Output: list of float (dense vector)
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

---

### 5.3 `database.py`

> **Storage:** ChromaDB dengan persistent storage. Data disimpan di folder `chroma_db/` dan akan tetap ada setelah program ditutup.

```python
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

---

### 5.4 `indexer.py`

> **Catatan:** Jalankan `indexer.py` **SATU KALI** untuk membangun database. Jika dataset bertambah, gunakan incremental insert (lihat Bagian 8.2).

```python
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

---

### 5.5 `searcher.py`

> **Logika:** Menerima judul dari UI → preprocess → embed → query Chroma → konversi distance ke similarity score → return Top-N hasil terurut.

```python
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

        Output: list of dict, contoh:
        [
          {
            'judul': 'Implementasi Algoritma ...',
            'mahasiswa': 'Budi Santoso',
            'tahun': '2022',
            'prodi': 'Teknik Informatika',
            'similarity': 0.87
          },
          ...
        ]
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

---

### 5.6 `app.py` — Streamlit UI

> **Frontend:** Streamlit digunakan sebagai interface web. Jalankan dengan: `streamlit run app.py`

```python
import streamlit as st
from modules.searcher import Searcher
import pandas as pd

# ─── Konfigurasi halaman ──────────────────────────────────────────
st.set_page_config(
    page_title='Deteksi Kemiripan Judul TA',
    page_icon='🎓',
    layout='wide'
)

# ─── Header ───────────────────────────────────────────────────────
st.title('🎓 Sistem Deteksi Kemiripan Judul Tugas Akhir')
st.markdown('Masukkan judul yang akan divalidasi untuk melihat kemiripan topik.')
st.divider()

# ─── Inisialisasi Searcher (cached agar tidak reload tiap run) ────
@st.cache_resource
def load_searcher():
    return Searcher()

searcher = load_searcher()

# ─── Form Input ───────────────────────────────────────────────────
input_title = st.text_input(
    label='Judul Tugas Akhir',
    placeholder='Contoh: Implementasi machine learning untuk deteksi...'
)

top_n = st.slider('Jumlah hasil yang ditampilkan', min_value=5, max_value=20, value=10)

if st.button('🔍 Cari Kemiripan', type='primary'):
    if input_title.strip() == '':
        st.warning('Masukkan judul terlebih dahulu.')
    else:
        with st.spinner('Memproses...'):
            results = searcher.search(input_title, top_n=top_n)

        st.success(f'Ditemukan {len(results)} judul dengan kemiripan tertinggi.')
        st.divider()

        # ─── Tampilkan hasil sebagai tabel ───────────────────────
        df_result = pd.DataFrame(results)
        df_result.index = df_result.index + 1   # mulai dari 1
        df_result.columns = ['Judul', 'Mahasiswa', 'Tahun', 'Prodi', 'Similarity']

        # Highlight baris dengan similarity tinggi
        st.dataframe(
            df_result.style.background_gradient(
                subset=['Similarity'], cmap='Blues'
            ),
            use_container_width=True
        )
```

---

## 6. Skema Database & Metadata Chroma

### 6.1 Informasi Collection

| Field | Detail |
|---|---|
| **Nama Collection** | `skripsi_embeddings` |
| **Distance Metric** | cosine (konfigurasi via `hnsw:space`) |
| **Tipe Embedding** | Dense float32 vector |
| **Dimensi Vector** | 1024 (output default bge-m3) |
| **Storage Location** | `./chroma_db/` (persistent, di disk lokal) |

---

### 6.2 Skema Metadata per Dokumen

| Field | Tipe Data | Keterangan | Contoh Nilai |
|---|---|---|---|
| `judul` | string | Judul lengkap tugas akhir (original) | Implementasi Deep Learning... |
| `mahasiswa` | string | Nama mahasiswa penulis | Budi Santoso |
| `tahun` | string | Tahun lulus / sidang | 2022 |
| `prodi` | string | Program studi / jurusan | Teknik Informatika |

> **Catatan:** ID dokumen menggunakan format `doc_0`, `doc_1`, dst. Untuk dataset yang diperbarui, gunakan ID unik lain (misal: NIM mahasiswa) agar tidak terjadi duplikasi.

---

### 6.3 Format Kolom Dataset Input (`.xlsx` / `.csv`)

| Nama Kolom | Tipe | Wajib? | Keterangan |
|---|---|---|---|
| `judul` | string | **Ya** | Judul tugas akhir lengkap |
| `abstrak` | string | **Ya** | Abstrak / ringkasan penelitian |
| `mahasiswa` | string | Tidak | Nama penulis (untuk metadata) |
| `tahun` | string/int | Tidak | Tahun tugas akhir |
| `prodi` | string | Tidak | Program studi |

---

## 7. Representasi Matematika Sistem

### 7.1 Representasi Dokumen

Untuk setiap dokumen `d` dalam database, representasi vektor dihitung sebagai:

```
T_doc  = Judul_d + " " + Abstrak_d      # Penggabungan teks
T_proc = preprocess(T_doc)              # Light cleaning
V_doc  = E(T_proc)                      # Dense vector via bge-m3
```

### 7.2 Representasi Query

```
T_input = Judul_input                   # Hanya judul dari user
T_proc  = preprocess(T_input)
V_input = E(T_proc)
```

### 7.3 Formula Cosine Similarity

```
                   A · B
Sim(A, B)  =  ──────────────
               ‖A‖ × ‖B‖

Dimana:
  A      = V_input  (vektor query)
  B      = V_doc    (vektor dokumen di database)
  A · B  = dot product
  ‖A‖    = norma Euclidean vektor A

Nilai output: 0.0 (tidak mirip) sampai 1.0 (identik secara semantik)
```

> **Catatan Teknis:** Karena `normalize_embeddings=True` diset saat encode, semua vektor sudah ternormalisasi (`‖V‖ = 1`). Cosine similarity otomatis setara dengan dot product, sehingga perhitungan lebih efisien.

---

## 8. Panduan Menjalankan Sistem

### 8.1 Urutan Langkah Pertama Kali *(First-Time Setup)*

1. Clone atau siapkan folder proyek sesuai struktur direktori di Bagian 4.1
2. Buat dan aktifkan virtual environment (lihat Bagian 3.2.1)
3. Install semua dependencies (lihat Bagian 3.2.3)
4. Siapkan file `dataset.xlsx` di folder `data/` dengan kolom yang sesuai (lihat Bagian 6.3)
5. Jalankan indexer untuk membangun database embedding:

```bash
python modules/indexer.py
# Proses ini membutuhkan waktu beberapa menit
# tergantung jumlah dokumen dan kecepatan GPU
```

6. Setelah indexing selesai, jalankan aplikasi Streamlit:

```bash
streamlit run app.py
```

7. Buka browser ke alamat yang ditampilkan (biasanya `http://localhost:8501`)

---

### 8.2 Menambah Dokumen Baru *(Incremental Update)*

Jika dataset bertambah, **tidak perlu rebuild semua index**. Gunakan fungsi insert langsung:

```python
from modules.preprocessor import combine_title_abstract
from modules.embedder import Embedder
from modules.database import VectorDatabase

embedder = Embedder()
db = VectorDatabase()

# Data dokumen baru
new_title    = 'Judul tugas akhir baru'
new_abstract = 'Abstrak tugas akhir baru...'
new_metadata = {'judul': new_title, 'mahasiswa': 'Nama', 'tahun': '2025', 'prodi': 'TI'}

# Embed dan simpan
combined  = combine_title_abstract(new_title, new_abstract)
embedding = embedder.embed(combined)
db.insert(doc_id='doc_601', embedding=embedding, metadata=new_metadata)
```

---

## 9. Batasan Sistem & Mitigasi Risiko

| Batasan | Dampak | Mitigasi |
|---|---|---|
| Bergantung kualitas abstrak | Abstrak kosong atau singkat menurunkan akurasi embedding | Validasi kolom abstrak tidak boleh kosong saat indexing |
| Bukan plagiarisme checker | Tidak mendeteksi kesamaan isi dokumen penuh | Beri disclaimer pada UI bahwa ini tools validasi topik awal |
| Threshold belum ditentukan | Keputusan "mirip atau tidak" masih subjektif | Lakukan eksperimen threshold secara empiris pada dataset |
| Model perlu GPU | Lambat di CPU, terutama saat indexing | Pastikan CUDA aktif; untuk CPU-only gunakan model lebih kecil |
| Tidak real-time update otomatis | Dokumen baru harus diindex manual | Buat script incremental insert; jadwalkan update periodik |

---

## 10. Ringkasan Keputusan Desain

| Keputusan | Pilihan | Alasan |
|---|---|---|
| Preprocessing | Light cleaning (bukan agresif) | Model bge-m3 sudah paham konteks; stemming merusak semantik |
| Representasi dokumen | Judul + Abstrak digabung | Konteks lebih kaya, satu vektor per dokumen, sederhana |
| Input pengguna | Judul saja | Sesuai alur akademik nyata; abstrak belum ada di tahap pengajuan |
| Metode similarity | Cosine Similarity | Standar semantic retrieval, tidak dipengaruhi panjang vektor |
| Vector database | Chroma | Cocok skala kecil-menengah, integrasi Python mudah, ada metadata |
| Frontend | Streamlit | Cepat prototyping, integrasi langsung Python, cocok NLP apps |
| Model embedding | bge-m3 (BAAI) | Multilingual (Bahasa Indonesia), state-of-the-art semantic retrieval |

---

*— Akhir Dokumen TRD-SKTA-2025 —*

*Dokumen ini dapat diperbarui seiring perkembangan implementasi.*
