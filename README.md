# Sistem Deteksi Kemiripan Judul Tugas Akhir

Sistem berbasis Vector Similarity Search untuk membantu dosen memvalidasi
kemiripan topik sebelum ACC judul tugas akhir.

## Stack Teknologi
- Python 3.11
- Model: BAAI/bge-m3 (via SentenceTransformers)
- Vector DB: ChromaDB
- Frontend: Streamlit

## Cara Menjalankan

1) Buat & aktifkan virtualenv

- Windows PowerShell:
	- `python -m venv venv`
	- `venv\Scripts\Activate.ps1`

2) Install dependency

- `pip install -r requirements.txt`

Catatan penting:
- Jika muncul error terkait **CVE-2025-32434** / "upgrade torch to at least v2.6", berarti `torch` Anda terlalu lama.
	Upgrade `torch`/`torchvision`/`torchaudio` ke versi >= 2.6.
	- CPU: `pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
	- CUDA 12.4: `pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124`

	Catatan: wheel `cu121` umumnya mentok di `torch 2.5.1`, jadi untuk `torch>=2.6` gunakan `cu124`.

3) Jalankan aplikasi

- `streamlit run app.py`
