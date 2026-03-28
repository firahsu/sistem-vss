import chromadb


class VectorDatabase:
	def __init__(self, persist_path: str = "./chroma_db"):
		self.client = chromadb.PersistentClient(path=persist_path)
		self.collection = self.client.get_or_create_collection(
			name="skripsi_embeddings",
			metadata={"hnsw:space": "cosine"},
		)

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

	def query(self, query_embedding: list, top_n: int = 10) -> dict:
		"""
		Query Top-N dokumen paling mirip.
		Output: dict berisi 'ids', 'distances', 'metadatas'

		CATATAN: Chroma cosine distance = 1 - cosine_similarity
		Untuk mendapatkan similarity score: similarity = 1 - distance
		"""
		results = self.collection.query(
			query_embeddings=[query_embedding],
			n_results=top_n,
			include=["metadatas", "distances"],
		)
		return results

	def count(self) -> int:
		"""Mengembalikan jumlah dokumen dalam database."""
		return self.collection.count()
