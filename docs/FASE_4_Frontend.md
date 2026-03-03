# 🖥️ FASE 4 — Frontend (Streamlit UI)

---

| Field | Detail |
|-------|--------|
| **Fase** | 4 dari 5 |
| **Status** | ⬜ Belum Dimulai |
| **Prasyarat** | [Fase 3](FASE_3_Logic_Layer.md) selesai dan checklist gate terpenuhi |
| **Fase Selanjutnya** | [Fase 5 — Integrasi & Testing](FASE_5_Integrasi_Testing.md) |
| **Referensi TRD** | Bagian 5.6 (app.py), Bagian 9 (Batasan & Disclaimer) |

> **Tujuan:** Implementasi antarmuka web menggunakan **Streamlit** agar dosen dapat melakukan pencarian kemiripan judul secara interaktif melalui browser. UI terhubung langsung ke modul `Searcher` yang sudah dibangun di Fase 3.

---

## Navigasi

[← Fase 3](FASE_3_Logic_Layer.md) · [PLANNING](PLANNING.md) · **Fase 4** · [Fase 5 →](FASE_5_Integrasi_Testing.md) · [Catatan Revisi](REVISION_NOTES.md)

---

## Daftar Isi Fase 4

1. [Gambaran UI & Komponen](#1-gambaran-ui--komponen)
2. [Implementasi app.py](#2-implementasi-apppy)
3. [Penjelasan Teknis Setiap Bagian](#3-penjelasan-teknis-setiap-bagian)
4. [Menjalankan Aplikasi](#4-menjalankan-aplikasi)
5. [Pengujian UI](#5-pengujian-ui)
6. [Checklist Gate — Sebelum Lanjut ke Fase 5](#6-checklist-gate--sebelum-lanjut-ke-fase-5)

---

## 1. Gambaran UI & Komponen

### 1.1 Layout Halaman

```
┌──────────────────────────────────────────────────────────────────┐
│  🎓 Sistem Deteksi Kemiripan Judul Tugas Akhir                  │
│  Masukkan judul yang akan divalidasi untuk melihat kemiripan     │
│  topik.                                                          │
│  ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  Judul Tugas Akhir:                                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Contoh: Implementasi machine learning untuk deteksi...     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Jumlah hasil yang ditampilkan:                                  │
│  ├────────●─────────────────────┤  10                            │
│  5                               20                              │
│                                                                  │
│  ┌──────────────────────┐                                        │
│  │  🔍 Cari Kemiripan   │                                        │
│  └──────────────────────┘                                        │
│                                                                  │
│  ─────────────────────────────────────────────────────────────── │
│  ✅ Ditemukan 10 judul dengan kemiripan tertinggi.               │
│                                                                  │
│  ┌────┬──────────────────┬──────────┬──────┬────────┬──────────┐│
│  │ No │ Judul            │Mahasiswa │Tahun │ Prodi  │Similarity││
│  ├────┼──────────────────┼──────────┼──────┼────────┼──────────┤│
│  │  1 │ Implementasi...  │ Budi S.  │ 2022 │ TI     │  0.9231  ││
│  │  2 │ Analisis...      │ Siti A.  │ 2023 │ SI     │  0.8547  ││
│  │ .. │ ...              │ ...      │ ...  │ ...    │  ...     ││
│  └────┴──────────────────┴──────────┴──────┴────────┴──────────┘│
│      Kolom Similarity menggunakan gradient warna (Blues)          │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Komponen UI

| No | Komponen | Tipe Streamlit | Fungsi |
|----|----------|----------------|--------|
| 1 | Header | `st.title()` + `st.markdown()` | Judul halaman dan deskripsi |
| 2 | Input Judul | `st.text_input()` | Field untuk memasukkan judul TA |
| 3 | Slider Top-N | `st.slider()` | Mengatur jumlah hasil (5-20, default 10) |
| 4 | Tombol Cari | `st.button()` | Memicu proses pencarian |
| 5 | Spinner | `st.spinner()` | Indikator loading saat proses |
| 6 | Pesan Sukses | `st.success()` | Menampilkan jumlah hasil ditemukan |
| 7 | Pesan Warning | `st.warning()` | Peringatan jika input kosong |
| 8 | Tabel Hasil | `st.dataframe()` | Menampilkan hasil dengan gradient warna |

### 1.3 Tentang Streamlit

| Aspek | Detail |
|-------|--------|
| **Apa itu** | Framework Python untuk membuat web app data science dengan cepat |
| **Cara kerja** | Script Python biasa, Streamlit me-render ulang dari atas ke bawah setiap interaksi |
| **Server** | Built-in (tidak perlu setup web server terpisah) |
| **Port default** | `http://localhost:8501` |
| **Hot reload** | Otomatis reload saat file berubah |

**Keputusan Desain (dari TRD Bagian 10):** Streamlit dipilih karena cepat untuk prototyping, integrasi langsung dengan Python, dan cocok untuk NLP apps.

---

## 2. Implementasi `app.py`

### 2.1 Kode Lengkap

```python
# app.py — Entry point Streamlit UI

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

## 3. Penjelasan Teknis Setiap Bagian

### 3.1 `st.set_page_config()`

```python
st.set_page_config(
    page_title='Deteksi Kemiripan Judul TA',   # judul tab browser
    page_icon='🎓',                              # favicon
    layout='wide'                                # gunakan lebar penuh
)
```

- **Wajib dipanggil pertama** di script (sebelum komponen lain)
- `layout='wide'` membuat tabel hasil lebih mudah dibaca

### 3.2 `@st.cache_resource`

```python
@st.cache_resource
def load_searcher():
    return Searcher()
```

**Mengapa penting:**
- Streamlit me-render ulang script **dari atas ke bawah** setiap kali ada interaksi
- Tanpa cache, `Searcher()` akan membuat `Embedder()` baru setiap klik → load model ~2.5 GB ulang
- `@st.cache_resource` memastikan `Searcher` hanya dibuat **satu kali** dan di-reuse

### 3.3 Input & Validasi

```python
input_title = st.text_input(
    label='Judul Tugas Akhir',
    placeholder='Contoh: Implementasi machine learning untuk deteksi...'
)
```

- `st.text_input()` mengembalikan string (kosong jika belum diisi)
- Validasi input kosong dilakukan sebelum proses pencarian
- `st.warning()` menampilkan pesan jika input kosong

### 3.4 Slider Top-N

```python
top_n = st.slider('Jumlah hasil yang ditampilkan', min_value=5, max_value=20, value=10)
```

- Range: 5 sampai 20 hasil
- Default: 10 (sesuai default `Searcher.search()`)
- User bisa geser untuk melihat lebih banyak/sedikit hasil

### 3.5 Proses Pencarian

```python
if st.button('🔍 Cari Kemiripan', type='primary'):
    ...
    with st.spinner('Memproses...'):
        results = searcher.search(input_title, top_n=top_n)
```

- `type='primary'` membuat tombol berwarna biru (menonjol)
- `st.spinner()` menampilkan loading indicator selama `searcher.search()` berjalan

### 3.6 Tampilan Tabel Hasil

```python
df_result = pd.DataFrame(results)
df_result.index = df_result.index + 1  # index mulai dari 1, bukan 0
df_result.columns = ['Judul', 'Mahasiswa', 'Tahun', 'Prodi', 'Similarity']

st.dataframe(
    df_result.style.background_gradient(subset=['Similarity'], cmap='Blues'),
    use_container_width=True
)
```

- Hasil dari `Searcher` dikonversi ke DataFrame pandas
- Index digeser +1 agar nomor baris dimulai dari 1
- `background_gradient(cmap='Blues')` memberikan warna gradient pada kolom Similarity:
  - Biru tua = similarity tinggi
  - Biru muda = similarity rendah
- `use_container_width=True` membuat tabel menggunakan lebar penuh

---

## 4. Menjalankan Aplikasi

### 4.1 Perintah

```powershell
# Pastikan berada di root proyek dan venv aktif
cd D:\.KULIAHKU\Bismillah\skripsi-similarity

# Jalankan Streamlit
streamlit run app.py
```

### 4.2 Output Terminal yang Diharapkan

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 4.3 Akses di Browser

1. Buka browser (Chrome/Edge disarankan)
2. Navigasi ke `http://localhost:8501`
3. Halaman aplikasi akan muncul

### 4.4 Menghentikan Aplikasi

Tekan `Ctrl+C` di terminal untuk menghentikan server Streamlit.

### 4.5 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `streamlit` not recognized | Pastikan venv aktif; atau jalankan `python -m streamlit run app.py` |
| Halaman kosong di browser | Tunggu beberapa detik — Streamlit sedang loading model pertama kali |
| Port 8501 sudah digunakan | Jalankan dengan port lain: `streamlit run app.py --server.port 8502` |
| Error saat klik tombol | Cek terminal untuk traceback — kemungkinan bug di `Searcher` atau `Database` |
| Model loading sangat lama | Normal untuk pertama kali (~30 detik); setelahnya akan ter-cache |

---

## 5. Pengujian UI

### Test 1: Input Kosong

| Langkah | Expected |
|---------|----------|
| Biarkan field judul kosong | — |
| Klik "🔍 Cari Kemiripan" | Muncul pesan warning: "Masukkan judul terlebih dahulu." |

### Test 2: Input Valid

| Langkah | Expected |
|---------|----------|
| Ketik: "Implementasi deep learning untuk klasifikasi citra" | — |
| Klik "🔍 Cari Kemiripan" | 1. Spinner "Memproses..." muncul |
| | 2. Pesan sukses: "Ditemukan X judul dengan kemiripan tertinggi." |
| | 3. Tabel hasil muncul dengan 5 kolom |
| | 4. Kolom Similarity memiliki gradient warna biru |

### Test 3: Slider Top-N

| Langkah | Expected |
|---------|----------|
| Geser slider ke 5 | — |
| Klik cari | Tabel menampilkan tepat 5 baris |
| Geser slider ke 20 | — |
| Klik cari | Tabel menampilkan tepat 20 baris (atau kurang jika database < 20) |

### Test 4: Responsivitas

| Langkah | Expected |
|---------|----------|
| Perkecil jendela browser | Tabel menyesuaikan lebar |
| Perbesar jendela browser | Tabel menggunakan lebar penuh |

### Test 5: Multiple Searches

| Langkah | Expected |
|---------|----------|
| Cari judul pertama | Hasil muncul |
| Ganti judul, cari lagi | Hasil berubah sesuai query baru |
| Cari 3-5 kali berturut-turut | Tidak ada error atau memory leak |

### Langkah — Checklist Pengujian

- [ ] **4.1** File `app.py` diimplementasi sesuai kode di atas
- [ ] **4.2** `streamlit run app.py` berjalan tanpa error
- [ ] **4.3** Halaman web terbuka di `http://localhost:8501`
- [ ] **4.4** Test 1 (input kosong) — warning muncul
- [ ] **4.5** Test 2 (input valid) — spinner, success, tabel muncul
- [ ] **4.6** Test 3 (slider) — jumlah baris berubah sesuai slider
- [ ] **4.7** Test 4 (responsif) — tabel menyesuaikan lebar
- [ ] **4.8** Test 5 (multiple searches) — tidak ada error

---

## 6. Checklist Gate — Sebelum Lanjut ke Fase 5

> **🚫 JANGAN LANJUT KE FASE 5 sebelum SEMUA item di bawah tercentang.**
>
> Jika ada yang gagal, perbaiki dulu dan catat masalahnya di [REVISION_NOTES.md](REVISION_NOTES.md).

### Fungsionalitas

- [ ] `streamlit run app.py` berjalan tanpa error di terminal
- [ ] Halaman web berhasil terbuka di browser (`http://localhost:8501`)
- [ ] Input judul kosong memunculkan pesan warning
- [ ] Input judul valid menampilkan tabel hasil pencarian
- [ ] Tabel memiliki 5 kolom: Judul, Mahasiswa, Tahun, Prodi, Similarity
- [ ] Slider Top-N berfungsi mengubah jumlah baris hasil
- [ ] Gradient warna biru muncul pada kolom Similarity

### Performa & UX

- [ ] Spinner "Memproses..." muncul saat pencarian berlangsung
- [ ] Pesan success muncul setelah pencarian selesai
- [ ] Pencarian berulang (3+ kali) tidak menyebabkan error
- [ ] Model tidak di-reload setiap pencarian (cache berfungsi)

### Verifikasi Akhir

Jalankan aplikasi, lakukan pencarian, dan pastikan hasilnya masuk akal:

```
1. streamlit run app.py
2. Buka http://localhost:8501
3. Input judul → klik Cari → lihat hasil
4. Ganti judul → klik Cari lagi → pastikan hasil berubah
5. Ctrl+C untuk stop
```

---

> **Fase 4 selesai?** Lanjut ke → [Fase 5 — Integrasi, Testing & Finalisasi](FASE_5_Integrasi_Testing.md)

---

*Referensi: TRD-SKTA-2025 Bagian 5.6 dan 9*
