# Sistem Deteksi Kemiripan Judul Tugas Akhir

Sistem berbasis Vector Similarity Search untuk membantu dosen memvalidasi
kemiripan topik sebelum ACC judul tugas akhir.

## Stack Teknologi
- Python 3.11
- Model: BAAI/bge-m3 (via SentenceTransformers)
- Vector DB: ChromaDB
- Frontend: Streamlit

## Cara Menjalankan

Berikut langkah singkat menjalankan proyek menggunakan virtual environment (`venv`) di Windows.

1) Buat dan aktifkan virtualenv

- PowerShell (direkomendasikan):
  - `python -m venv venv`
  - `venv\Scripts\Activate.ps1`

- CMD (jika tidak pakai PowerShell):
  - `python -m venv venv`
  - `venv\Scripts\activate.bat`

2) Install dependensi

- `pip install -r requirements.txt`

3) (Jika perlu) Perbaiki masalah `torch`

- Jika muncul error terkait **CVE-2025-32434** atau peringatan bahwa `torch` harus >= 2.6, jalankan salah satu perintah berikut sesuai kebutuhan lingkungan Anda:
  - CPU: `pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
  - CUDA 12.4: `pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124`

4) Menjalankan aplikasi Streamlit (dengan `venv` aktif)

- `streamlit run app.py`

5) Menjalankan server webhook (jalankan di terminal terpisah, dengan `venv` aktif)

- `python webhook_server.py`

Contoh alur di PowerShell (dua terminal):

Terminal 1 (Streamlit):

``powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
``

Terminal 2 (Webhook server):

``powershell
venv\Scripts\Activate.ps1
python webhook_server.py
``

Catatan:
- Pastikan kedua terminal menggunakan `venv` yang sama agar dependensi konsisten.
- Jika server webhook membutuhkan port atau konfigurasi lain, sesuaikan `webhook_server.py` atau gunakan variabel environment.

