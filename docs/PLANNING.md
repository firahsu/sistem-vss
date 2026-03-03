# 📋 PLANNING — Sistem Deteksi Kemiripan Judul TA
### Berdasarkan TRD-SKTA-2025

---

> **Petunjuk Penggunaan:**
> - Kerjakan fase secara **berurutan** (Fase 1 → 2 → 3 → 4 → 5)
> - Setiap fase memiliki **file tersendiri** dengan penjelasan teknis lengkap — klik link di bawah
> - Sebelum berpindah ke fase berikutnya, **semua item checklist gate** di fase sebelumnya harus tercentang ✅
> - Catat semua saran, revisi, atau temuan di file [REVISION_NOTES.md](REVISION_NOTES.md)

---

## Status Keseluruhan

| Fase | Nama | File Detail | Status |
|------|------|-------------|--------|
| 1 | Setup Environment & Struktur Proyek | [FASE_1_Setup_Environment.md](FASE_1_Setup_Environment.md) | ⬜ Belum Dimulai |
| 2 | Backend Core (Preprocessing + Embedding + Database) | [FASE_2_Backend_Core.md](FASE_2_Backend_Core.md) | ⬜ Belum Dimulai |
| 3 | Logic Layer (Indexer + Searcher) | [FASE_3_Logic_Layer.md](FASE_3_Logic_Layer.md) | ⬜ Belum Dimulai |
| 4 | Frontend (Streamlit UI) | [FASE_4_Frontend.md](FASE_4_Frontend.md) | ⬜ Belum Dimulai |
| 5 | Integrasi, Testing & Finalisasi | [FASE_5_Integrasi_Testing.md](FASE_5_Integrasi_Testing.md) | ⬜ Belum Dimulai |

> **Legenda Status:** ⬜ Belum Dimulai · 🔄 Sedang Dikerjakan · ✅ Selesai

---

## Ringkasan Setiap Fase

### [Fase 1 — Setup Environment & Struktur Proyek](FASE_1_Setup_Environment.md)

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Menyiapkan lingkungan kerja, venv, dependensi, dan struktur folder |
| **Yang dihasilkan** | Folder proyek lengkap, venv aktif, semua library terinstall, dataset siap |
| **Referensi TRD** | Bagian 3 (Setup Environment), Bagian 4.1 (Struktur Direktori) |
| **Jumlah langkah** | 18 langkah + checklist gate |

### [Fase 2 — Backend Core](FASE_2_Backend_Core.md)

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Implementasi preprocessor, embedder, dan database wrapper |
| **Yang dihasilkan** | 3 modul fungsional: `preprocessor.py`, `embedder.py`, `database.py` |
| **Referensi TRD** | Bagian 5.1, 5.2, 5.3, 6 (Skema DB), 7 (Matematika) |
| **Jumlah langkah** | 20 langkah + checklist gate |

### [Fase 3 — Logic Layer](FASE_3_Logic_Layer.md)

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Implementasi indexer dan searcher |
| **Yang dihasilkan** | 2 modul fungsional: `indexer.py`, `searcher.py` + database terisi |
| **Referensi TRD** | Bagian 5.4, 5.5, 2.2 (Alur Data), 7 (Matematika) |
| **Jumlah langkah** | 14 langkah + checklist gate |

### [Fase 4 — Frontend](FASE_4_Frontend.md)

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Implementasi antarmuka web Streamlit |
| **Yang dihasilkan** | `app.py` yang berjalan di browser |
| **Referensi TRD** | Bagian 5.6 |
| **Jumlah langkah** | 8 langkah + checklist gate |

### [Fase 5 — Integrasi, Testing & Finalisasi](FASE_5_Integrasi_Testing.md)

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Testing end-to-end, edge cases, incremental update, dokumentasi |
| **Yang dihasilkan** | Sistem final yang teruji + README lengkap + disclaimer |
| **Referensi TRD** | Bagian 8, 8.2, 9, 10 |
| **Jumlah langkah** | 15 langkah + checklist final |

---

## Dokumen Pendukung

| File | Fungsi |
|------|--------|
| [REVISION_NOTES.md](REVISION_NOTES.md) | Catatan revisi, saran, bug, dan ide (format terstruktur) |
| [TRD-SKTA-2025](../TRD_Sistem_Deteksi_Kemiripan_Judul_TA.md) | Dokumen acuan teknis utama |

---

## Catatan Penting

1. **Jangan loncat fase** — setiap fase membangun fondasi untuk fase berikutnya
2. **Buka file fase** untuk melihat langkah-langkah detail, kode, dan pengujian
3. **Jika menemukan masalah**, catat di [REVISION_NOTES.md](REVISION_NOTES.md) dengan kategori dan prioritas
4. **Jika ada perubahan dari TRD**, catat juga di `REVISION_NOTES.md` sebagai keputusan desain
5. **Backup folder `chroma_db/`** setelah indexing berhasil (selesai Fase 3)

---

*Dokumen ini dibuat berdasarkan TRD-SKTA-2025 versi 1.0*
*Terakhir diperbarui: 2025-03-03*
