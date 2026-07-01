import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
 
pd.set_option("display.max_colwidth", 60)
 
# ============================================================
# 1. SIAPKAN DATA CONTOH (judul + metadata)
# ============================================================
data_contoh = [
    {
        "id": "doc_001",
        "judul": "IMPLEMENTASI ALGORITMA JARO-WINKLER DISTANCE UNTUK KOREKSI EJAAN DALAM INSTITUTIONAL REPOSITORY UIN ALAUDDIN MAKASSAR",
        "abstrak": "Hasil penelitian menunjukkan bahwa algoritma Jaro-Winkler dapat memberikan saran ejaan yang baik, membantu orang menemukan informasi dengan lebih baik, dan membuat karya ilmiah dalam repositori lebih mudah diakses",
        "mahasiswa": "Nasrullah",
        "tahun": "2026",
        "prodi": "Teknik Informatika",
    },
    {
        "id": "doc_002",
        "judul": "Game Edukasi Sistem Gerak Manusia Untuk Siswa Kelas Xi Sekolah Menengah Atas",
        "abstrak": "Pembelajaran Sistem Gerak Manusia Di Sma Sering Kali Terbatas Pada Metode Ceramah Dan Buku Teks, Sehingga Siswa Kurang Tertarik Dan Sulit Memahami Konsep Secara Mendalam. Materi Yang Bersifat Abstrak Membutuhkan Media Yang Mampu Menghadirkan Visualisasi Dan Interaktivitas Agar Lebih Mudah Dipahami",
        "mahasiswa": "Rizki Fauziah",
        "tahun": "2026",
        "prodi": "Sistem Informasi",
    },
]
 
# ============================================================
# 2. LOAD MODEL EMBEDDING (bge-m3, 1024 dimensi)
# ============================================================
print("Memuat model embedding bge-m3 ...")
model = SentenceTransformer("BAAI/bge-m3")
 
# ============================================================
# 3. SETUP CHROMADB (lokal, in-memory / persistent)
# ============================================================
client = chromadb.PersistentClient(path="./chroma_demo_db")
collection = client.get_or_create_collection(name="skripsi_demo")
 
# ============================================================
# 4. PROSES EMBEDDING + SIMPAN KE CHROMADB
# ============================================================
for item in data_contoh:
    teks_gabungan = f"{item['judul']} {item['abstrak']}"
    vektor = model.encode(teks_gabungan).tolist()  # -> list 1024 angka float
 
    collection.add(
        ids=[item["id"]],
        embeddings=[vektor],
        metadatas=[{
            "judul": item["judul"],
            "abstrak": item["abstrak"],
            "mahasiswa": item["mahasiswa"],
            "tahun": item["tahun"],
            "prodi": item["prodi"],
        }],
    )
    print(f"-> Tersimpan: {item['id']} | dimensi vektor: {len(vektor)}")
 
# ============================================================
# 5. AMBIL KEMBALI DATA DARI CHROMADB (bukti penyimpanan nyata)
# ============================================================
hasil = collection.get(
    ids=[item["id"] for item in data_contoh],
    include=["embeddings", "metadatas"],
)
 
# ============================================================
# 6. TAMPILKAN DALAM BENTUK TABEL
# ============================================================
def format_vektor(vec, n_awal=5, n_akhir=5):
    """Tampilkan beberapa angka awal dan akhir vektor saja (karena 1024 angka tidak mungkin ditampilkan utuh di tabel)."""
    awal = ", ".join(f"{x:.4f}" for x in vec[:n_awal])
    akhir = ", ".join(f"{x:.4f}" for x in vec[-n_akhir:])
    return f"[{awal}, ..., {akhir}]  (total {len(vec)} dimensi)"
 
rows = []
for idx, meta, emb in zip(hasil["ids"], hasil["metadatas"], hasil["embeddings"]):
    rows.append({
        "ID": idx,
        "Judul": meta["judul"],
        "Mahasiswa": meta["mahasiswa"],
        "Tahun": meta["tahun"],
        "Prodi": meta["prodi"],
        "Vektor Numerik (1024 dim)": format_vektor(emb),
    })
 
df = pd.DataFrame(rows)
 
print("\n" + "=" * 100)
print("TABEL HASIL PENYIMPANAN VEKTOR + METADATA DI CHROMADB")
print("=" * 100)
print(df.to_string(index=False))
 
# Simpan juga ke CSV/Excel agar mudah di-screenshot / dilampirkan ke skripsi
df.to_csv("hasil_vektor_chromadb.csv", index=False)
print("\nTabel juga disimpan ke 'hasil_vektor_chromadb.csv'")
 
# ============================================================
# 7. (OPSIONAL) TAMPILKAN VEKTOR PENUH SATU DOKUMEN SEBAGAI CONTOH
# ============================================================
print("\n" + "=" * 100)
print(f"CONTOH VEKTOR PENUH UNTUK '{data_contoh[0]['id']}' (10 angka pertama dari 1024):")
print("=" * 100)
print(hasil["embeddings"][0][:10])
