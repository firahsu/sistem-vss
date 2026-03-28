import pandas as pd
import streamlit as st

from modules.searcher import Searcher


st.set_page_config(
	page_title="Deteksi Kemiripan Judul TA",
	page_icon="🎓",
	layout="wide",
)

st.title("🎓 Sistem Deteksi Kemiripan Judul Tugas Akhir")
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
		with st.spinner("Memproses..."):
			results = searcher.search(input_title, top_n=top_n)

		if not results:
			st.warning("Tidak ada data yang bisa ditampilkan. Pastikan database sudah terisi.")
		else:
			st.success(f"Ditemukan {len(results)} judul dengan kemiripan tertinggi.")
			st.divider()

			df_result = pd.DataFrame(results)
			df_result.index = df_result.index + 1
			df_result.columns = ["Judul", "Mahasiswa", "Tahun", "Prodi", "Similarity"]

			st.dataframe(
				df_result.style.background_gradient(subset=["Similarity"], cmap="Blues"),
				width="stretch",
			)
