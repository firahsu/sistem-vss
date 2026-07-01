import pandas as pd
import streamlit as st
import re
from datetime import datetime

import os
import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


st.set_page_config(
	page_title="Deteksi Kemiripan Judul TA",
	page_icon="🎓",
	layout="wide",
)

if "is_admin" not in st.session_state:
	st.session_state["is_admin"] = False
if "show_login" not in st.session_state:
	st.session_state["show_login"] = False


class RemoteDB:
	"""Menggantikan VectorDatabase — semua panggilan lewat HTTP ke FastAPI."""

	def __init__(self, base_url: str):
		self.base_url = base_url

	def count(self) -> int:
		resp = requests.get(f"{self.base_url}/status", timeout=10)
		resp.raise_for_status()
		return resp.json().get("total_documents", 0)

	def get_all(self) -> dict:
		resp = requests.get(f"{self.base_url}/documents", timeout=15)
		resp.raise_for_status()
		return resp.json()

	def get_sync_stats(self) -> dict:
		resp = requests.get(f"{self.base_url}/sync-stats", timeout=10)
		resp.raise_for_status()
		return resp.json()

	def delete(self, doc_id: str):
		resp = requests.delete(f"{self.base_url}/documents/{doc_id}", timeout=10)
		resp.raise_for_status()
		return resp.json()
	
	def get_all_logs(self) -> dict:
		resp = requests.get(f"{self.base_url}/logs", timeout=15)
		resp.raise_for_status()
		return resp.json()



class SearcherClient:
	"""Menggantikan Searcher — TIDAK load model apa pun, murni HTTP client."""

	def __init__(self, base_url: str):
		self.base_url = base_url
		self.db = RemoteDB(base_url)

	def search(self, input_title: str, top_n: int = 10) -> list[dict]:
		resp = requests.post(
			f"{self.base_url}/search",
			json={"judul": input_title, "top_n": top_n},
			timeout=30,
		)
		resp.raise_for_status()
		return resp.json().get("results", [])


@st.cache_resource
def load_searcher() -> SearcherClient:
	return SearcherClient(API_BASE_URL)


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


def format_timestamp(value):
	if not value:
		return "-"
	try:
		return datetime.fromisoformat(str(value).replace("Z", "+00:00")).strftime("%d-%m-%Y %H:%M:%S")
	except Exception:
		return str(value)


def get_sync_stats_safe(searcher):
	db = searcher.db
	getter = getattr(db, "get_sync_stats", None)
	if callable(getter):
		try:
			return getter()
		except Exception as exc:
			st.warning(f"Gagal memuat statistik sinkronisasi: {exc}")

	return {
		"total_documents": db.count() if hasattr(db, "count") else 0,
		"total_logs": 0,
		"total_records": db.count() if hasattr(db, "count") else 0,
		"status_counts": {},
		"source_counts": {},
		"form_submit_count": 0,
		"daily_sync_count": 0,
		"initial_index_count": 0,
		"latest_sync_at": None,
	}


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

	stats = get_sync_stats_safe(searcher)
	tab_list, tab_log, tab_sync, tab_delete = st.tabs(["📋 Daftar Judul", "🧾 Log Status", "📈 Info Sinkronisasi", "🗑️ Hapus Data"])

	with tab_list:
		st.subheader("Daftar Data Tersimpan")
		if st.button("Refresh Data"):
			st.rerun()

		data_res = searcher.db.get_all()
		ids = data_res.get("ids", [])
		metas = data_res.get("metadatas", [])

		if ids:
			table_data = []
			for i, (idx, m) in enumerate(zip(ids, metas), 1):
				metadata = m or {}
				table_data.append({
					"No": i,
					"ID Dokumen": idx,
					"Judul": metadata.get("judul", "-"),
					"Mahasiswa": metadata.get("nama", metadata.get("mahasiswa", "-")),
					"Tahun": metadata.get("tahun", "-"),
					"Prodi": metadata.get("jurusan", metadata.get("prodi", "-")),
					"Status": metadata.get("status", "success"),
					"Sumber": metadata.get("source", "initial_index"),
					"Ditambahkan": format_timestamp(metadata.get("synced_at") or metadata.get("created_at")),
				})

			df_display = pd.DataFrame(table_data)
			st.dataframe(df_display, use_container_width=True)
			st.caption(f"Total ada {len(ids)} dokumen yang tersimpan.")
		else:
			st.info("Belum ada data di database.")

	with tab_log:
		st.subheader("Log Status Sinkronisasi")
		log_filter = st.selectbox("Filter status", ["all", "success", "duplicate", "failed"], index=0)
		log_res = searcher.db.get_all_logs()
		log_ids = log_res.get("ids", [])
		log_metas = log_res.get("metadatas", [])

		log_rows = []
		for i, (idx, metadata) in enumerate(zip(log_ids, log_metas), 1):
			meta = metadata or {}
			status = meta.get("status", "failed")
			if log_filter != "all" and status != log_filter:
				continue
			log_rows.append({
				"No": i,
				"Log ID": idx,
				"Status": status,
				"Sumber": meta.get("source", "unknown"),
				"Mahasiswa": meta.get("nama", "-"),
				"Judul": meta.get("judul", "-"),
				"Tahun": meta.get("tahun", "-"),
				"Pesan": meta.get("message", "-"),
				"Terkait": meta.get("related_doc_id", meta.get("attempt_doc_id", "-")),
				"Waktu": format_timestamp(meta.get("synced_at") or meta.get("created_at")),
			})

		if log_rows:
			st.dataframe(pd.DataFrame(log_rows), use_container_width=True)
		else:
			st.info("Belum ada log sinkronisasi untuk filter ini.")

	with tab_sync:
		st.subheader("Info Sinkronisasi")
		col1, col2, col3, col4 = st.columns(4)
		col1.metric("Total Dokumen", stats.get("total_documents", 0))
		col2.metric("Dari Form", stats.get("form_submit_count", 0))
		col3.metric("Dari Sync Harian", stats.get("daily_sync_count", 0))
		col4.metric("Index Awal", stats.get("initial_index_count", 0))

		st.divider()
		st.write("**Status Ringkasan**")
		status_counts = stats.get("status_counts", {})
		status_df = pd.DataFrame([
			{"Status": key, "Jumlah": value}
			for key, value in status_counts.items()
		])
		st.dataframe(status_df, use_container_width=True, hide_index=True)

		st.write("**Sumber Sinkronisasi**")
		source_counts = stats.get("source_counts", {})
		source_df = pd.DataFrame([
			{"Sumber": key, "Jumlah": value}
			for key, value in source_counts.items()
		])
		st.dataframe(source_df, use_container_width=True, hide_index=True)

		st.caption(f"Sinkronisasi terakhir: {format_timestamp(stats.get('latest_sync_at'))}")

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
	sidebar_stats = get_sync_stats_safe(searcher)
	st.caption(f"📁 {total_data} judul tersimpan")
	st.caption(f"⏱️ Sinkronisasi terakhir: {format_timestamp(sidebar_stats.get('latest_sync_at'))}")

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
