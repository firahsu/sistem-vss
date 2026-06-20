import re
from datetime import datetime

import chromadb


class VectorDatabase:
	def __init__(self, persist_path: str = "./chroma_db"):
		self.client = chromadb.PersistentClient(path=persist_path)
		self.collection = self.client.get_or_create_collection(
			name="skripsi_embeddings",
			metadata={"hnsw:space": "cosine"},
		)
		self.log_collection = self.client.get_or_create_collection(
			name="skripsi_sync_logs",
			metadata={"hnsw:space": "cosine"},
		)

	@staticmethod
	def _normalize_text(value: str | None) -> str:
		return re.sub(r"\s+", " ", str(value or "")).strip().lower()

	@staticmethod
	def _parse_timestamp(value: str | None) -> datetime | None:
		if not value:
			return None

		candidate = str(value).strip()
		if not candidate:
			return None

		try:
			return datetime.fromisoformat(candidate.replace("Z", "+00:00"))
		except ValueError:
			return None

	def insert(self, doc_id: str, embedding: list, metadata: dict):
		"""
		Menyimpan satu dokumen ke Chroma.
		metadata contoh: {'judul': '...', 'mahasiswa': '...', 'tahun': '...', 'prodi': '...'}
		"""
		self.collection.add(
			ids=[doc_id],
			embeddings=[embedding],
			metadatas=[metadata],
		)

	def insert_batch(self, doc_ids: list, embeddings: list, metadatas: list):
		"""
		Menyimpan banyak dokumen sekaligus (lebih efisien).
		"""
		self.collection.add(
			ids=doc_ids,
			embeddings=embeddings,
			metadatas=metadatas,
		)

	def insert_log(self, log_id: str, metadata: dict, embedding_dim: int = 1024):
		"""Menyimpan log sinkronisasi ke koleksi terpisah."""
		self.log_collection.add(
			ids=[log_id],
			embeddings=[[0.0] * embedding_dim],
			metadatas=[metadata],
		)

	def query(self, query_embedding: list, top_n: int = 10, where: dict | None = None) -> dict:
		"""
		Query Top-N dokumen paling mirip.
		Output: dict berisi 'ids', 'distances', 'metadatas'

		CATATAN: Chroma cosine distance = 1 - cosine_similarity
		Untuk mendapatkan similarity score: similarity = 1 - distance
		"""
		results = self.collection.query(
			query_embeddings=[query_embedding],
			n_results=top_n,
			where=where,
			include=["metadatas", "distances"],
		)
		return results

	def count(self) -> int:
		"""Mengembalikan jumlah dokumen dalam database."""
		return self.collection.count()

	def get_all(self):
		"""Mengambil semua dokumen."""
		return self.collection.get(include=["metadatas"])

	def get_all_logs(self):
		"""Mengambil semua log sinkronisasi."""
		return self.log_collection.get(include=["metadatas"])

	def check_duplicate(self, judul: str, nama: str, tahun: str) -> tuple[bool, str | None]:
		"""Cek duplikasi berdasarkan judul, nama, dan tahun."""
		judul_clean = str(judul or "").strip()
		nama_clean = str(nama or "").strip()
		tahun_clean = str(tahun or "").strip()

		if not judul_clean or not nama_clean or not tahun_clean:
			return False, None

		results = self.collection.get(
			where={
				"$and": [
					{"judul": judul_clean},
					{"nama": nama_clean},
					{"tahun": tahun_clean},
				],
			},
			include=["metadatas"],
		)
		ids = results.get("ids", [])
		if ids:
			return True, ids[0]

		normalized_target = (
			self._normalize_text(judul_clean),
			self._normalize_text(nama_clean),
			self._normalize_text(tahun_clean),
		)

		legacy_results = self.collection.get(include=["metadatas"])
		for doc_id, metadata in zip(legacy_results.get("ids", []), legacy_results.get("metadatas", [])):
			metadata = metadata or {}

			candidate = (
				self._normalize_text(metadata.get("judul")),
				self._normalize_text(metadata.get("nama", metadata.get("mahasiswa"))),
				self._normalize_text(metadata.get("tahun")),
			)
			if candidate == normalized_target:
				return True, doc_id

		return False, None

	def get_sync_stats(self) -> dict:
		"""Ringkasan statistik sinkronisasi untuk admin panel."""
		data_results = self.collection.get(include=["metadatas"])
		data_ids = data_results.get("ids", [])
		data_metadatas = data_results.get("metadatas", [])
		log_results = self.log_collection.get(include=["metadatas"])
		log_ids = log_results.get("ids", [])
		log_metadatas = log_results.get("metadatas", [])

		status_counts = {"success": 0, "duplicate": 0, "failed": 0}
		source_counts = {"form_submit": 0, "daily_sync": 0, "initial_index": 0}
		total_data = 0
		total_logs = 0
		latest_sync_at = None

		for metadata in data_metadatas:
			metadata = metadata or {}
			status = metadata.get("status", "success")
			source = metadata.get("source", "initial_index")
			timestamp_value = metadata.get("synced_at") or metadata.get("created_at")

			total_data += 1

			if status in status_counts:
				status_counts[status] += 1
			else:
				status_counts[status] = 1

			if source in source_counts:
				source_counts[source] += 1
			else:
				source_counts[source] = 1

			parsed_timestamp = self._parse_timestamp(timestamp_value)
			if parsed_timestamp and (latest_sync_at is None or parsed_timestamp > latest_sync_at):
				latest_sync_at = parsed_timestamp

		for metadata in log_metadatas:
			metadata = metadata or {}
			status = metadata.get("status", "failed")
			source = metadata.get("source", "unknown")
			timestamp_value = metadata.get("synced_at") or metadata.get("created_at")

			total_logs += 1

			if status in status_counts:
				status_counts[status] += 1
			else:
				status_counts[status] = 1

			if source in source_counts:
				source_counts[source] += 1
			else:
				source_counts[source] = 1

			parsed_timestamp = self._parse_timestamp(timestamp_value)
			if parsed_timestamp and (latest_sync_at is None or parsed_timestamp > latest_sync_at):
				latest_sync_at = parsed_timestamp

		return {
			"total_documents": total_data,
			"total_logs": total_logs,
			"total_records": len(data_ids) + len(log_ids),
			"status_counts": status_counts,
			"source_counts": source_counts,
			"form_submit_count": source_counts.get("form_submit", 0),
			"daily_sync_count": source_counts.get("daily_sync", 0),
			"initial_index_count": source_counts.get("initial_index", 0),
			"latest_sync_at": latest_sync_at.isoformat() if latest_sync_at else None,
		}

	def delete(self, doc_id: str):
		"""Menghapus dokumen berdasarkan ID."""
		self.collection.delete(ids=[doc_id])
		try:
			log_results = self.log_collection.get(include=["metadatas"])
			log_ids = log_results.get("ids", [])
			log_metadatas = log_results.get("metadatas", [])
			matching_log_ids = []
			for log_id, metadata in zip(log_ids, log_metadatas):
				metadata = metadata or {}
				if metadata.get("attempt_doc_id") == doc_id or metadata.get("related_doc_id") == doc_id:
					matching_log_ids.append(log_id)

			if matching_log_ids:
				self.log_collection.delete(ids=matching_log_ids)
		except Exception:
			pass

