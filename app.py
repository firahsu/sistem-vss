import pandas as pd
import streamlit as st
import re

from modules.searcher import Searcher
from modules.preprocessor import combine_title_abstract

st.set_page_config(
	page_title="Deteksi Kemiripan Judul TA",
	page_icon="🎓",
	layout="wide",
)

if "is_admin" not in st.session_state:
	st.session_state["is_admin"] = False
if "show_login" not in st.session_state:
	st.session_state["show_login"] = False


@st.cache_resource
def load_searcher() -> Searcher:
	return Searcher()


def do_login(username, password):
	if username == "admin" and password == "admin123":
		st.session_state["is_admin"] = True
		st.session_state["show_login"] = False
		return True
	return False


def do_logout():
	st.session_state["is_admin"] = False
	st.session_state["show_login"] = False
	st.rerun()


def highlight_matching_words(query: str, result_title: str) -> str:
	stopwords = {
		"dan", "atau", "yang", "di", "ke", "dari", 
		"untuk", "dengan", "pada", "dalam", "adalah", 
		"ini", "itu", "sebuah", "suatu", "sebagai", 
		"oleh", "sistem", "berbasis", "menggunakan"
	}
	
	query_words = set(re.findall(r'\b\w+\b', query.lower()))
	query_words = query_words - stopwords
	
	def repl(match):
		word = match.group(0)
		if word.lower() in query_words:
			return f'<mark style="background-color:#FFD700; border-radius:3px; padding:0 3px; font-weight:bold;">{word}</mark>'
		return word
		
	return re.sub(r'\b\w+\b', repl, result_title)


def page_login():
	st.title("🔑 Login Sistem")
	with st.form("login_form"):
		username = st.text_input("Username")
		password = st.text_input("Password", type="password")
		submit = st.form_submit_button("Login")

		if submit:
			if do_login(username, password):
				st.success("Login berhasil!")
				st.rerun()
			else:
				st.error("Username atau password salah")


def page_pencarian(searcher):
	st.title("🎓 Sistem Deteksi Kemiripan Judul Tugas Akhir")
	st.markdown("Masukkan judul yang akan divalidasi untuk melihat kemiripan topik.")
	st.divider()

	input_title = st.text_input(
		label="Judul Tugas Akhir",
		placeholder="Contoh: Implementasi machine learning untuk deteksi...",
	)

	top_n = st.slider("Jumlah hasil yang ditampilkan", min_value=5, max_value=20, value=10)

	if st.button("🔍 Cari Kemiripan", type="primary"):
		if input_title.strip() == "":
			st.warning("Masukkan judul terlebih dahulu.")
		else:
			with st.status(
				"Sedang mencari kemiripan... mohon tunggu, jangan klik tombol berulang.",
				expanded=True,
			) as search_status:
				st.write("Memproses input judul dan menghitung embedding...")
				results = searcher.search(input_title, top_n=top_n)
				st.write("Menyiapkan hasil untuk ditampilkan...")
				search_status.update(label="Pencarian selesai.", state="complete", expanded=False)

			if not results:
				st.warning("Tidak ada data yang bisa ditampilkan. Pastikan database sudah terisi.")
			else:
				st.success(f"Ditemukan {len(results)} judul dengan kemiripan tertinggi.")
				st.divider()

				for index, row in enumerate(results, 1):
					with st.expander(f"{index}. {row['judul']} - Kemiripan: {row['similarity'] * 100:.2f}%"):
						highlighted_title = highlight_matching_words(input_title, row['judul'])
						st.markdown(f"**Judul:** {highlighted_title}", unsafe_allow_html=True)
						st.caption(f"Mahasiswa: {row['mahasiswa']} | Tahun: {row['tahun']} | Prodi: {row['prodi']}")
						st.write("**Abstrak:**")
						st.write(row['abstrak'])


def page_manajemen(searcher):
	st.title("⚙️ Manajemen Data Tugas Akhir")

	tab_list, tab_delete = st.tabs(["📋 Daftar Judul", "🗑️ Hapus Data"])

	with tab_list:
		st.subheader("Daftar Data Tersimpan")
		if st.button("Refresh Data"):
			pass

		data_res = searcher.db.get_all()
		ids = data_res.get("ids", [])
		metas = data_res.get("metadatas", [])

		if ids:
			table_data = []
			for i, (idx, m) in enumerate(zip(ids, metas), 1):
				table_data.append({
					"No": i,
					"ID Dokumen": idx,
					"Judul": m.get("judul", "-"),
					"Mahasiswa": m.get("nama", m.get("mahasiswa", "-")),  # Map 'nama' from webhook
					"Tahun": m.get("tahun", "-"),
					"Prodi": m.get("jurusan", m.get("prodi", "-"))  # Map 'jurusan' from webhook
				})

			df_display = pd.DataFrame(table_data)
			st.dataframe(df_display, use_container_width=True)
			st.caption(f"Total ada {len(ids)} dokumen yang tersimpan.")
		else:
			st.info("Belum ada data di database.")

	with tab_delete:
		st.subheader("Hapus Data Dokumen")
		doc_id_to_delete = st.text_input("Masukkan ID Dokumen")
		if st.button("Hapus"):
			if doc_id_to_delete.strip():
				try:
					searcher.db.delete(doc_id_to_delete.strip())
					st.success("Dokumen berhasil dihapus." )
				except Exception as e:
					st.error(f"Gagal menghapus dokumen: {e}")
			else:
				st.warning("Masukkan ID dokumen terlebih dahulu.")


# MAIN EXECUTION

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


# Sidebar Config
with st.sidebar:
	st.markdown("## 🔍 Sistem Deteksi")
	st.markdown("**Kemiripan Judul TA**")
	st.divider()

	total_data = searcher.db.count()
	st.caption(f"📁 {total_data} judul tersimpan")

	if st.session_state["is_admin"]:
		st.markdown("⚙️ **Administrator | admin**")
		st.divider()
		if st.button("🚪 Logout", use_container_width=True, type="primary"):
			do_logout()
	else:
		st.divider()
		if st.button("⚙️ Admin", type="secondary"):
			st.session_state["show_login"] = not st.session_state["show_login"]
			st.rerun()

# Routing Content
if st.session_state["is_admin"]:
	page_manajemen(searcher)
else:
	if st.session_state["show_login"]:
		page_login()
	else:
		page_pencarian(searcher)
