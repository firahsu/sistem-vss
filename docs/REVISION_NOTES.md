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
| RN-001 | 2025-03-03 | Umum | Catatan Teknis | 🟢 Rendah | ⬜ Baru | Contoh entri — hapus setelah entri pertama dibuat |

---

## Entri Catatan

---

### RN-001

| Field | Isi |
|-------|-----|
| **ID** | RN-001 |
| **Tanggal** | 2025-03-03 |
| **Fase Terkait** | Umum |
| **Kategori** | Catatan Teknis |
| **Prioritas** | 🟢 Rendah |
| **Status** | ⬜ Baru |
| **Judul** | Contoh entri — hapus setelah entri pertama dibuat |
| **Detail** | Ini adalah contoh format entri catatan revisi. Hapus entri ini dan ganti dengan catatan asli Anda saat mulai bekerja. Setiap catatan baru ditambahkan di bawah entri terakhir dengan ID berurutan. |
| **Tindakan** | Hapus entri ini saat entri pertama yang sesungguhnya dibuat |
| **Resolusi** | — |

---

<!-- 
=============================================
TAMBAHKAN ENTRI BARU DI BAWAH BARIS INI
Salin template dari bagian "Template Entri" 
dan tambahkan separator (---) sebelum entri
=============================================
-->
