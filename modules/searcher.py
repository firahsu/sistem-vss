from modules.database import VectorDatabase
from modules.embedder import Embedder
from modules.preprocessor import preprocess_text


class Searcher:
	def __init__(self):
		self.embedder = Embedder()
		self.db = VectorDatabase()

	def search(self, input_title: str, top_n: int = 10) -> list[dict]:
		"""
		Menerima judul input, mengembalikan Top-N hasil kemiripan.

		Output: list of dict dengan keys: judul, mahasiswa, tahun, prodi, similarity
		Terurut dari similarity tertinggi ke terendah.
		"""
		clean_input = preprocess_text(input_title or "")
		if not clean_input:
			return []

		available_docs = self.db.count()
		if available_docs == 0:
			return []

		limit = max(1, min(int(top_n), available_docs))
		query_vector = self.embedder.embed(clean_input)
		raw_results = self.db.query(query_vector, top_n=limit)

		ids = raw_results.get("ids", [[]])[0]
		distances = raw_results.get("distances", [[]])[0]
		metadatas = raw_results.get("metadatas", [[]])[0]

		results = []
		for index in range(len(ids)):
			metadata = metadatas[index] or {}
			similarity_score = max(0.0, min(1.0, 1 - distances[index]))

			results.append(
				{
					"judul": metadata.get("judul", "-"),
					"abstrak": metadata.get("abstrak", "Abstrak tidak tersedia."),
					"mahasiswa": metadata.get("mahasiswa", "-"),
					"tahun": metadata.get("tahun", "-"),
					"prodi": metadata.get("prodi", "-"),
					"similarity": round(similarity_score, 4),
				}
			)

		results.sort(key=lambda item: item["similarity"], reverse=True)
		return results
