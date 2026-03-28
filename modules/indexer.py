from pathlib import Path

import pandas as pd

from modules.database import VectorDatabase
from modules.embedder import Embedder
from modules.preprocessor import combine_title_abstract


COLUMN_ALIASES = {
	"judul": "judul",
	"judul skripsi": "judul",
	"abstrak": "abstrak",
	"mahasiswa": "mahasiswa",
	"nama": "mahasiswa",
	"tahun": "tahun",
	"prodi": "prodi",
	"jurusan": "prodi",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
	rename_map = {}

	for column in df.columns:
		normalized_name = str(column).strip().lower()
		if normalized_name in COLUMN_ALIASES:
			rename_map[column] = COLUMN_ALIASES[normalized_name]

	df = df.rename(columns=rename_map)
	missing_columns = [column for column in ("judul", "abstrak") if column not in df.columns]

	if missing_columns:
		raise KeyError(
			"Kolom wajib tidak ditemukan di dataset: "
			+ ", ".join(missing_columns)
		)

	return df


def _stringify_value(value) -> str:
	if pd.isna(value):
		return "-"

	if isinstance(value, float) and value.is_integer():
		return str(int(value))

	text = str(value).strip()
	return text if text else "-"


def _load_dataset(dataset_path: str) -> pd.DataFrame:
	dataset_file = Path(dataset_path)
	if not dataset_file.exists():
		raise FileNotFoundError(f"Dataset tidak ditemukan: {dataset_file}")

	last_error = None
	for header_row in (0, 1):
		try:
			df = pd.read_excel(dataset_file, header=header_row)
			df = _normalize_columns(df)
			break
		except KeyError as error:
			last_error = error
	else:
		raise last_error or KeyError("Kolom dataset tidak sesuai format yang didukung.")

	for column in ("judul", "abstrak", "mahasiswa", "tahun", "prodi"):
		if column not in df.columns:
			df[column] = None

	df["judul"] = df["judul"].apply(_stringify_value)
	df["abstrak"] = df["abstrak"].apply(_stringify_value)

	df = df[(df["judul"] != "-") & (df["abstrak"] != "-")].reset_index(drop=True)
	if df.empty:
		raise ValueError("Dataset tidak memiliki baris valid dengan kolom judul dan abstrak.")

	return df


def _reset_collection_if_needed(db: VectorDatabase) -> VectorDatabase:
	current_count = db.count()
	if current_count == 0:
		return db

	collection_name = db.collection.name
	print(f"[Indexer] Database sudah berisi {current_count} dokumen. Rebuild koleksi...")
	db.client.delete_collection(collection_name)
	return VectorDatabase()


def build_index(dataset_path: str = "./data/dataset.xlsx"):
	"""
	Membaca dataset dan membangun index embedding di Chroma.
	Jalankan satu kali saat pertama setup atau saat rebuild database.
	"""
	df = _load_dataset(dataset_path)
	embedder = Embedder()
	db = _reset_collection_if_needed(VectorDatabase())

	print(f"[Indexer] Memproses {len(df)} dokumen valid...")

	combined_texts = []
	doc_ids = []
	metadatas = []

	for idx, row in df.iterrows():
		combined_texts.append(
			combine_title_abstract(row["judul"], row["abstrak"])
		)
		doc_ids.append(f"doc_{idx}")
		metadatas.append(
			{
				"judul": _stringify_value(row.get("judul")),
				"mahasiswa": _stringify_value(row.get("mahasiswa")),
				"tahun": _stringify_value(row.get("tahun")),
				"prodi": _stringify_value(row.get("prodi")),
			}
		)

	embeddings = embedder.embed_batch(combined_texts, batch_size=16)
	db.insert_batch(doc_ids, embeddings, metadatas)
	print(f"[Indexer] Selesai. Total dokumen: {db.count()}")


if __name__ == "__main__":
	build_index()
