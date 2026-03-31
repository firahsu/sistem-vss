import time
import pandas as pd
import streamlit as st

from modules.searcher import Searcher


st.set_page_config(
	page_title="Deteksi Kemiripan Judul TA",
	page_icon="🎓",
	layout="wide",
)

st.title("🎓 Sistem Deteksi Kemiripan Judul Tugas Akhir by FF")
st.markdown("Masukkan judul yang akan divalidasi untuk melihat kemiripan topik.")
st.divider()


@st.cache_resource
def load_searcher() -> Searcher:
	return Searcher()


searcher = None
init_error = None

try:
	searcher = load_searcher()
except Exception as exc:
	init_error = exc

if init_error is not None:
	st.error(
		"Gagal menginisialisasi model embedding. Cek koneksi internet atau cache model HuggingFace, lalu refresh halaman."
	)
	st.caption(f"Detail teknis: {init_error}")
	st.stop()

input_title = st.text_input(
	label="Judul Tugas Akhir",
	placeholder="Contoh: Implementasi machine learning untuk deteksi...",
)

top_n = st.slider("Jumlah hasil yang ditampilkan", min_value=5, max_value=20, value=10)

if st.button("🔍 Cari Kemiripan", type="primary"):
	if input_title.strip() == "":
		st.warning("Masukkan judul terlebih dahulu.")
	else:
		start_time = time.time()
		with st.status(
			"Sedang mencari kemiripan... mohon tunggu, jangan klik tombol berulang.",
			expanded=True,
		) as search_status:
			st.write("Memproses input judul dan menghitung embedding...")
			results = searcher.search(input_title, top_n=top_n)
			st.write("Menyiapkan hasil untuk ditampilkan...")
			duration = time.time() - start_time
			search_status.update(label=f"Pencarian selesai ({duration:.2f} detik).", state="complete", expanded=False)

		if not results:
			st.warning("Tidak ada data yang bisa ditampilkan. Pastikan database sudah terisi.")
		else:
			st.success(f"Ditemukan {len(results)} judul dengan kemiripan tertinggi dalam {duration:.2f} detik.")
			st.divider()

			# Menampilkan hasil dengan bentuk accordion (expander)
			for idx, item in enumerate(results, start=1):
				sim_percentage = item["similarity"] * 100
				
				# Menentukan icon berdasarkan seberapa mirip
				if sim_percentage >= 80:
					icon = "🔴" # Sangat mirip
				elif sim_percentage >= 60:
					icon = "🟠" # Lumayan mirip
				else:
					icon = "🟢" # Aman

				with st.expander(f"{icon} #{idx} — Similiarity: {sim_percentage:.1f}% — {item['judul']}", expanded=idx==1):
					col1, col2 = st.columns([1, 2])
					with col1:
						st.markdown(f"**Mahasiswa:** {item['mahasiswa']}")
						st.markdown(f"**Program Studi:** {item['prodi']}")
						st.markdown(f"**Tahun:** {item['tahun']}")
						st.progress(float(item["similarity"]), text=f"Tingkat Kemiripan ({sim_percentage:.1f}%)")
					
					with col2:
						# Menampilkan button/expand abstrak
						abstrak_text = item.get("abstrak", "Abstrak tidak tersedia.")
						if abstrak_text == "-" or not abstrak_text.strip():
							abstrak_text = "*Abstrak belum diinputkan pada data.* \n\n *(Catatan: Anda perlu mengindex ulang atau menjalankan merge/indexer lagi jika baru saja mengubah kode indexer)*"

						st.markdown("**Abstrak:**")
						st.info(abstrak_text)
