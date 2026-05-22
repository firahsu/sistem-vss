from sentence_transformers import SentenceTransformer
import torch
from huggingface_hub.utils import close_session


class Embedder:
	def __init__(self, model_name: str = "BAAI/bge-m3"):
		self.device = "cuda" if torch.cuda.is_available() else "cpu"
		print(f"[Embedder] Menggunakan device: {self.device}")
		self.model = self._load_model_with_retry(model_name)

	def _load_model_with_retry(self, model_name: str) -> SentenceTransformer:
		"""
		Load model dengan retry ringan untuk menangani error intermiten
		`httpx client has been closed` dari huggingface_hub.
		"""
		base_kwargs = {"use_safetensors": False}  # Use PyTorch format instead of safetensors

		for attempt in range(2):
			try:
				return SentenceTransformer(
					model_name,
					device=self.device,
					model_kwargs=base_kwargs,
				)
			except RuntimeError as exc:
				message = str(exc).lower()
				if "client has been closed" not in message:
					raise

				print(
					f"[Embedder] HuggingFace HTTP client tertutup (attempt {attempt + 1}/2). Ulangi inisialisasi..."
				)
				close_session()

		# Fallback: gunakan cache lokal agar startup tetap berjalan ketika koneksi tidak stabil.
		print("[Embedder] Beralih ke local_files_only=True (cache lokal).")
		return SentenceTransformer(
			model_name,
			device=self.device,
			model_kwargs={**base_kwargs, "local_files_only": True},
		)

	def embed(self, text: str) -> list[float]:
		"""
		Generate embedding untuk satu string.
		Output: list of float (dense vector, dimensi 1024)
		"""
		vector = self.model.encode(
			text,
			normalize_embeddings=True,
			show_progress_bar=False,
		)
		return vector.tolist()

	def embed_batch(self, texts: list[str], batch_size: int = 32) -> list:
		"""
		Generate embedding untuk banyak teks sekaligus (lebih efisien).
		"""
		vectors = self.model.encode(
			texts,
			batch_size=batch_size,
			normalize_embeddings=True,
			show_progress_bar=True,
		)
		return [vector.tolist() for vector in vectors]
