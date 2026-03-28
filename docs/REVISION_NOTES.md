# 📝 REVISION NOTES — Sistem Deteksi Kemiripan Judul TA

---

> **Dokumen ini digunakan untuk mencatat:**
> - Saran revisi yang muncul selama implementasi
> - Catatan teknis yang tidak tercakup dalam TRD
> - Keputusan desain yang berbeda dari TRD asli
> - Bug yang ditemukan dan solusinya
> - Ide pengembangan di masa depan
>
> **Referensi:** [PLANNING.md](PLANNING.md) · [TRD-SKTA-2025](../TRD_Sistem_Deteksi_Kemiripan_Judul_TA.md)

---

## Cara Mengisi Catatan

Setiap entri menggunakan format tabel berikut. **Salin template di bawah** untuk menambah entri baru.

### Template Entri

```markdown
| Field | Isi |
|-------|-----|
| **ID** | RN-XXX |
| **Tanggal** | YYYY-MM-DD |
| **Fase Terkait** | Fase X — Nama Fase |
| **Kategori** | [Bug / Saran / Perubahan Desain / Catatan Teknis / Ide Pengembangan] |
| **Prioritas** | [🔴 Tinggi / 🟡 Sedang / 🟢 Rendah] |
| **Status** | [⬜ Baru / 🔄 Sedang Ditangani / ✅ Selesai / ❌ Ditolak] |
| **Judul** | Deskripsi singkat (1 baris) |
| **Detail** | Penjelasan lengkap masalah / saran / catatan |
| **Tindakan** | Langkah yang perlu diambil (kosongkan jika belum ada) |
| **Resolusi** | Hasil akhir setelah ditindaklanjuti (isi saat status = Selesai/Ditolak) |
```

### Penjelasan Field

| Field | Deskripsi |
|-------|-----------|
| **ID** | Nomor urut unik. Format: `RN-001`, `RN-002`, dst. |
| **Tanggal** | Tanggal catatan dibuat, format `YYYY-MM-DD` |
| **Fase Terkait** | Fase mana yang relevan (Fase 1–5), atau "Umum" jika lintas fase |
| **Kategori** | Salah satu dari: `Bug`, `Saran`, `Perubahan Desain`, `Catatan Teknis`, `Ide Pengembangan` |
| **Prioritas** | 🔴 Tinggi = harus segera, 🟡 Sedang = penting tapi tidak mendesak, 🟢 Rendah = nice-to-have |
| **Status** | ⬜ Baru, 🔄 Sedang Ditangani, ✅ Selesai, ❌ Ditolak (dengan alasan) |
| **Judul** | Ringkasan 1 baris untuk identifikasi cepat |
| **Detail** | Penjelasan lengkap, bisa termasuk langkah reproduksi (untuk bug), alasan (untuk saran), dsb. |
| **Tindakan** | Apa yang perlu dilakukan untuk menyelesaikan catatan ini |
| **Resolusi** | Diisi saat catatan sudah selesai atau ditolak. Jelaskan apa yang dilakukan atau alasan penolakan |

---

## Daftar Ringkasan

> Tabel ini diperbarui setiap kali ada entri baru untuk memudahkan tracking.

| ID | Tanggal | Fase | Kategori | Prioritas | Status | Judul |
|----|---------|------|----------|-----------|--------|-------|
| RN-001 | 2026-03-07 | Fase 1 | Perubahan Desain | 🟡 Sedang | ✅ Selesai | Lokasi proyek berbeda dari TRD |
| RN-002 | 2026-03-07 | Fase 1 | Catatan Teknis | 🟡 Sedang | ✅ Selesai | Python 3.11.6 digunakan (bukan default system 3.13) |
| RN-003 | 2026-03-07 | Fase 1 | Catatan Teknis | 🟢 Rendah | ✅ Selesai | CUDA Toolkit tidak diinstall terpisah — nvcc tidak tersedia |
| RN-004 | 2026-03-07 | Fase 1 — Fase 2 | Perubahan Desain | 🔴 Tinggi | ⬜ Baru | Dataset kolom tidak sesuai format TRD — perlu mapping |
| RN-005 | 2026-03-07 | Fase 1 | Catatan Teknis | 🟢 Rendah | ✅ Selesai | Dataset hanya 35 baris (TRD optimasi untuk ±600) |
| RN-006 | 2026-03-07 | Fase 1 | Catatan Teknis | 🟢 Rendah | ✅ Selesai | Execution Policy harus diubah ke RemoteSigned |
| RN-007 | 2026-03-14 | Fase 2 | Catatan Teknis | 🟡 Sedang | ✅ Selesai | Embedder dipaksa load safetensors untuk kompatibilitas transformers terbaru |
| RN-008 | 2026-03-14 | Fase 2 | Bug | 🔴 Tinggi | ✅ Selesai | Workspace sempat memakai env Python 3.13 yang salah — CUDA tidak terdeteksi |
| RN-009 | 2026-03-15 | Fase 1 — Fase 3 | Catatan Teknis | 🟡 Sedang | ✅ Selesai | Dataset memiliki banyak baris kosong sehingga indexer perlu memfilter dokumen valid |
| RN-010 | 2026-03-15 | Umum (lintas fase) | Catatan Teknis | 🟡 Sedang | ✅ Selesai | Penambahan dependency global matplotlib saat eksekusi Fase 4 |
| RN-011 | 2026-03-15 | Umum (lintas fase) | Catatan Teknis | 🟡 Sedang | ✅ Selesai | Migrasi parameter `st.dataframe` karena deprecation Streamlit |

---

## Entri Catatan

---

### RN-001

| Field | Isi |
|-------|-----|
| **ID** | RN-001 |
| **Tanggal** | 2026-03-07 |
| **Fase Terkait** | Fase 1 — Setup Environment |
| **Kategori** | Perubahan Desain |
| **Prioritas** | 🟡 Sedang |
| **Status** | ✅ Selesai |
| **Judul** | Lokasi proyek berbeda dari TRD |
| **Detail** | TRD dan Fase 1 menetapkan lokasi proyek di `D:\.KULIAHKU\Bismillah\skripsi-similarity\`. Atas permintaan pengguna, lokasi proyek diubah menjadi `D:\.KULIAHKU\Bismillah\vss\` (workspace yang sudah ada). Struktur internal folder tetap sama sesuai TRD (modules/, data/, chroma_db/, dll). |
| **Tindakan** | Pastikan semua path referensi di fase selanjutnya menggunakan lokasi baru |
| **Resolusi** | Proyek dibuat di `D:\.KULIAHKU\Bismillah\vss\` sesuai keputusan pengguna. Tidak ada dampak fungsional. |

---

### RN-002

| Field | Isi |
|-------|-----|
| **ID** | RN-002 |
| **Tanggal** | 2026-03-07 |
| **Fase Terkait** | Fase 1 — Setup Environment |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟡 Sedang |
| **Status** | ✅ Selesai |
| **Judul** | Python 3.11.6 digunakan (bukan default system 3.13) |
| **Detail** | Sistem memiliki Python 3.13.12 sebagai default. TRD merekomendasikan Python 3.10 atau 3.11. Python 3.13 belum sepenuhnya didukung oleh beberapa library (torch, chromadb, dll). Python 3.11.6 diinstall secara terpisah di `C:\Program Files\Python311\`. Virtual environment dibuat menggunakan Python 3.11.6 secara eksplisit. |
| **Tindakan** | Selalu gunakan venv saat bekerja — jangan gunakan Python system (3.13) |
| **Resolusi** | venv berhasil dibuat dengan Python 3.11.6. Semua library kompatibel. |

---

### RN-003

| Field | Isi |
|-------|-----|
| **ID** | RN-003 |
| **Tanggal** | 2026-03-07 |
| **Fase Terkait** | Fase 1 — Setup Environment |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟢 Rendah |
| **Status** | ✅ Selesai |
| **Judul** | CUDA Toolkit tidak diinstall terpisah — nvcc tidak tersedia |
| **Detail** | Fase 1 Langkah 4 mengharuskan instalasi CUDA Toolkit terpisah dan verifikasi `nvcc --version`. CUDA Toolkit **tidak diinstall** karena PyTorch versi cu121 sudah membawa CUDA runtime sendiri. `nvidia-smi` menunjukkan driver CUDA 12.7 yang kompatibel. `torch.cuda.is_available()` mengembalikan `True`. |
| **Tindakan** | Tidak perlu install CUDA Toolkit terpisah kecuali ada kebutuhan kompilasi CUDA kernel khusus |
| **Resolusi** | PyTorch cu121 berjalan normal tanpa CUDA Toolkit terpisah. Checklist 1.9 (nvcc) diskip. |

---

### RN-004

| Field | Isi |
|-------|-----|
| **ID** | RN-004 |
| **Tanggal** | 2026-03-07 |
| **Fase Terkait** | Fase 1 — Fase 2 (lintas fase) |
| **Kategori** | Perubahan Desain |
| **Prioritas** | 🔴 Tinggi |
| **Status** | ✅ Selesai |
| **Judul** | Dataset kolom tidak sesuai format TRD — perlu mapping |
| **Detail** | Dataset `data/dataset.xlsx` memiliki format kolom berbeda dari TRD. Header berada di baris ke-2 (perlu `header=1` saat `pd.read_excel`). Mapping kolom yang diperlukan: `"Judul Skripsi"` → `judul`, `"Abstrak"` → `abstrak`, `"Nama"` → `mahasiswa`, `"Tahun"` → `tahun`, `"Jurusan"` → `prodi`. Kolom `"No"` tidak diperlukan. |
| **Tindakan** | Di Fase 3, tambahkan logika pembacaan dataset yang mencoba header standar lalu fallback ke `header=1`, sekaligus mapping kolom otomatis di `indexer.py`. |
| **Resolusi** | `modules/indexer.py` sekarang memetakan header dataset aktual ke format internal TRD secara otomatis, sehingga file Excel saat ini bisa di-index tanpa mengubah sumber data. |

---

### RN-005

| Field | Isi |
|-------|-----|
| **ID** | RN-005 |
| **Tanggal** | 2026-03-07 |
| **Fase Terkait** | Fase 1 — Setup Environment |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟢 Rendah |
| **Status** | ✅ Selesai |
| **Judul** | Dataset hanya 35 baris (TRD optimasi untuk ±600) |
| **Detail** | Dataset saat ini hanya berisi 35 baris data. TRD menyebutkan sistem dioptimalkan untuk ±600 dokumen. Ini tidak menghalangi fungsi sistem, tetapi hasil pencarian kemiripan mungkin kurang representatif dengan dataset kecil. |
| **Tindakan** | Dataset bisa ditambah kapan saja. Tidak memblok implementasi. |
| **Resolusi** | Diterima — dataset 35 baris cukup untuk development dan testing awal. |

---

### RN-006

| Field | Isi |
|-------|-----|
| **ID** | RN-006 |
| **Tanggal** | 2026-03-07 |
| **Fase Terkait** | Fase 1 — Setup Environment |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟢 Rendah |
| **Status** | ✅ Selesai |
| **Judul** | Execution Policy harus diubah ke RemoteSigned |
| **Detail** | PowerShell default execution policy memblokir aktivasi venv (`Activate.ps1`). Diperlukan perintah `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` untuk mengizinkan eksekusi script lokal. Ini hanya perlu dilakukan sekali per user. |
| **Tindakan** | — |
| **Resolusi** | Execution policy sudah diubah. Venv bisa diaktivasi normal. |

---

### RN-007

| Field | Isi |
|-------|-----|
| **ID** | RN-007 |
| **Tanggal** | 2026-03-14 |
| **Fase Terkait** | Fase 2 — Backend Core |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟡 Sedang |
| **Status** | ✅ Selesai |
| **Judul** | Embedder dipaksa load safetensors untuk kompatibilitas transformers terbaru |
| **Detail** | Implementasi awal `SentenceTransformer(model_name, device=...)` gagal saat load `pytorch_model.bin` karena versi `transformers` terbaru memblok `torch.load` untuk `torch < 2.6` (environment memakai `torch 2.5.1+cu121`). |
| **Tindakan** | Ubah inisialisasi embedder menjadi `SentenceTransformer(..., model_kwargs={'use_safetensors': True})` agar model dimuat dari `model.safetensors` tanpa jalur `torch.load` yang diblokir. |
| **Resolusi** | Embedder berhasil load di GPU (`cuda`), test dimensi 1024, normalisasi vektor, dan batch embedding semuanya lulus. |

---

### RN-008

| Field | Isi |
|-------|-----|
| **ID** | RN-008 |
| **Tanggal** | 2026-03-14 |
| **Fase Terkait** | Fase 2 — Backend Core |
| **Kategori** | Bug |
| **Prioritas** | 🔴 Tinggi |
| **Status** | ✅ Selesai |
| **Judul** | Workspace sempat memakai env Python 3.13 yang salah — CUDA tidak terdeteksi |
| **Detail** | Saat menjalankan checklist gate Fase 2, pengujian sempat memakai `.venv` / `.venv-1` yang ternyata berbasis Python 3.13.12 dan tidak memiliki paket `torch`, sehingga gate embedder sebelumnya jatuh ke kondisi CPU / non-CUDA. Setelah diaudit, environment proyek yang benar sesuai Fase 1 adalah `venv` (Python 3.11.6) dan di dalamnya sudah terpasang `torch 2.5.1+cu121`, `torchvision 0.20.1+cu121`, dan `torchaudio 2.5.1+cu121`. |
| **Tindakan** | Set workspace Python environment ke `D:\.KULIAHKU\Bismillah\vss\venv\Scripts\python.exe`, lalu verifikasi ulang `torch.cuda.is_available()`, nama GPU, dan gate `Embedder`. |
| **Resolusi** | Workspace diarahkan ke `venv` yang benar. Verifikasi menunjukkan `torch 2.5.1+cu121`, `torch.cuda.is_available() = True`, GPU terdeteksi sebagai `NVIDIA GeForce RTX 4050 Laptop GPU`, dan gate embedder lulus penuh dengan output `device: cuda`. |

---

### RN-009

| Field | Isi |
|-------|-----|
| **ID** | RN-009 |
| **Tanggal** | 2026-03-15 |
| **Fase Terkait** | Fase 1 — Fase 3 |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟡 Sedang |
| **Status** | ✅ Selesai |
| **Judul** | Dataset memiliki banyak baris kosong sehingga indexer perlu memfilter dokumen valid |
| **Detail** | Saat verifikasi Fase 3, `data/dataset.xlsx` terbaca 35 baris setelah `header=1`, tetapi 17 di antaranya adalah baris kosong penuh. Akibatnya, jumlah dokumen yang benar-benar memiliki pasangan `judul` dan `abstrak` hanya 17. Jika semua baris diproses tanpa filter, indexer akan menghasilkan embedding untuk data tidak valid. |
| **Tindakan** | Tambahkan filter di `indexer.py` untuk hanya memproses baris dengan `judul` dan `abstrak` yang terisi. Pembersihan file Excel tetap disarankan bila dataset diperbarui. |
| **Resolusi** | Indexer sekarang otomatis membuang baris kosong / tidak valid sebelum proses embedding, sehingga jumlah dokumen yang di-index sesuai data yang benar-benar bisa digunakan. |

---

### RN-010

| Field | Isi |
|-------|-----|
| **ID** | RN-010 |
| **Tanggal** | 2026-03-15 |
| **Fase Terkait** | Umum (lintas fase) |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟡 Sedang |
| **Status** | ✅ Selesai |
| **Judul** | Penambahan dependency global matplotlib saat eksekusi Fase 4 |
| **Detail** | Saat validasi UI Fase 4, komponen `st.dataframe(df.style.background_gradient(..., cmap='Blues'))` gagal karena `pandas` membutuhkan paket `matplotlib` untuk styling gradient. Perubahan dilakukan pada `requirements.txt` (file global/lintas fase), di luar file spesifik Fase 4. |
| **Tindakan** | Tambahkan `matplotlib>=3.8.0` ke `requirements.txt` dan install pada environment aktif proyek. |
| **Resolusi** | Dependensi `matplotlib` berhasil ditambahkan dan diinstall. Uji otomatis UI Fase 4 kembali lulus (warning input kosong, hasil pencarian valid, slider Top-N, dan multiple searches). |

---

### RN-011

| Field | Isi |
|-------|-----|
| **ID** | RN-011 |
| **Tanggal** | 2026-03-15 |
| **Fase Terkait** | Umum (lintas fase) |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟡 Sedang |
| **Status** | ✅ Selesai |
| **Judul** | Migrasi parameter `st.dataframe` karena deprecation Streamlit |
| **Detail** | Saat verifikasi ulang gate Fase 4 pada environment `streamlit 1.55.0`, muncul warning deprecation bahwa `use_container_width` akan dihapus setelah 2025-12-31. Karena saat ini sudah 2026-03-15, konfigurasi UI perlu dimigrasi agar tetap kompatibel pada rilis Streamlit terbaru. Perubahan ini bersifat maintenance lintas fase (di luar implementasi awal Fase 4). |
| **Tindakan** | Ubah pemanggilan `st.dataframe(..., use_container_width=True)` menjadi `st.dataframe(..., width='stretch')` di `app.py`, lalu verifikasi ulang test UI otomatis. |
| **Resolusi** | `app.py` berhasil dimigrasi ke API baru (`width='stretch'`) dan verifikasi ulang checklist gate Fase 4 tetap lulus tanpa mengubah perilaku fungsional UI. |

---

<!-- 
=============================================
TAMBAHKAN ENTRI BARU DI BAWAH BARIS INI
Salin template dari bagian "Template Entri" 
dan tambahkan separator (---) sebelum entri
=============================================
-->
