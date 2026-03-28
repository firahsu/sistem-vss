import re


def preprocess_text(text: str) -> str:
	"""
	Light text cleaning untuk input embedding.
	Input : string (judul atau gabungan judul+abstrak)
	Output: string bersih
	"""
	text = text.lower()
	text = re.sub(r"[^a-z0-9\s]", " ", text)
	text = re.sub(r"\s+", " ", text)
	text = text.strip()
	return text


def combine_title_abstract(title: str, abstract: str) -> str:
	"""
	Menggabungkan judul dan abstrak sebelum di-embed.
	Strategi: judul + spasi + abstrak
	"""
	combined = title + " " + abstract
	return preprocess_text(combined)
