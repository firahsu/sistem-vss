"""
Webhook Server untuk otomatisasi input data dari Google Form → Google Sheets → Apps Script.
Endpoint POST /webhook menerima data judul skripsi, embedding, dan menyimpannya ke ChromaDB.
"""

import logging
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from modules.database import VectorDatabase
from modules.embedder import Embedder
from modules.preprocessor import combine_title_abstract


# ============================================================================
# Setup Logging
# ============================================================================
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================
class SubmissionData(BaseModel):
	"""Schema untuk data yang diterima dari Google Form (via Apps Script)."""
	nama: str
	judul: str
	abstrak: str
	jurusan: str
	tahun: str


class SubmissionResponse(BaseModel):
	"""Schema untuk response webhook."""
	status: str
	id: str
	pesan: str


# ============================================================================
# FastAPI App
# ============================================================================
app = FastAPI(
	title="VSS Webhook Server",
	description="Otomatisasi input data dari Google Form ke ChromaDB",
	version="1.0.0",
)


# ============================================================================
# Singleton instances untuk Embedder dan Database
# ============================================================================
_embedder = None
_database = None


def get_embedder() -> Embedder:
	"""Lazy load Embedder (singleton)."""
	global _embedder
	if _embedder is None:
		logger.info("[Webhook] Inisialisasi Embedder...")
		_embedder = Embedder()
	return _embedder


def get_database() -> VectorDatabase:
	"""Lazy load VectorDatabase (singleton)."""
	global _database
	if _database is None:
		logger.info("[Webhook] Inisialisasi VectorDatabase...")
		_database = VectorDatabase()
	return _database


# ============================================================================
# Helper: Insert single document
# ============================================================================
def insert_single_document(
	nama: str,
	judul: str,
	abstrak: str,
	jurusan: str,
	tahun: str,
) -> tuple[str, str]:
	"""
	Wrapper untuk insert satu dokumen ke ChromaDB.
	Menggabungkan: preprocessor.combine_title_abstract() + embedder.embed() + database.insert()

	Args:
		nama: Nama mahasiswa
		judul: Judul skripsi
		abstrak: Abstrak skripsi
		jurusan: Jurusan/Program studi
		tahun: Tahun akademik

	Returns:
		tuple (doc_id, pesan_status)

	Raises:
		Exception: Jika terjadi error saat embedding atau insert
	"""
	# Generate unique document ID dengan timestamp + UUID
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	unique_id = str(uuid.uuid4())[:8]
	doc_id = f"doc_{timestamp}_{unique_id}"

	try:
		# Step 1: Preprocessing & kombinasi judul + abstrak
		logger.info(f"[Webhook] Processing doc_id={doc_id}, judul={judul[:50]}...")
		combined_text = combine_title_abstract(judul, abstrak)

		# Step 2: Generate embedding menggunakan bge-m3 (dimensi 1024)
		logger.info(f"[Webhook] Starting embedding for {doc_id}...")
		embedder = get_embedder()
		logger.info(f"[Webhook] Embedder loaded, generating embedding...")
		try:
			embedding = embedder.embed(combined_text)
			logger.info(f"[Webhook] Embedding generated, dimensi={len(embedding)}")
		except Exception as emb_error:
			logger.error(f"[Webhook] Embedding error: {str(emb_error)}", exc_info=True)
			raise

		# Step 3: Siapkan metadata
		metadata = {
			"nama": str(nama).strip() or "-",
			"judul": str(judul).strip() or "-",
			"abstrak": str(abstrak).strip() or "-",
			"jurusan": str(jurusan).strip() or "-",
			"tahun": str(tahun).strip() or "-",
			"created_at": datetime.now().isoformat(),
		}

		# Step 4: Insert ke ChromaDB
		db = get_database()
		db.insert(doc_id, embedding, metadata)
		logger.info(f"[Webhook] Dokumen berhasil disimpan: {doc_id}")

		return doc_id, f"Dokumen '{judul[:50]}...' berhasil disimpan ke ChromaDB"

	except Exception as exc:
		error_msg = f"Error processing {doc_id}: {str(exc)}"
		logger.error(f"[Webhook] {error_msg}", exc_info=True)
		raise


# ============================================================================
# Endpoints
# ============================================================================
@app.on_event("startup")
async def startup_event():
	"""Initialize embedder saat server startup untuk avoid lazy loading di request pertama."""
	logger.info("[Webhook] Initializing embedder at startup...")
	try:
		embedder = get_embedder()
		logger.info("[Webhook] ✓ Embedder loaded successfully at startup")
	except Exception as exc:
		logger.warning(f"[Webhook] ⚠️  Embedder failed to load at startup (offline mode). "
					  f"Will attempt lazy-load on first request. Error: {str(exc)[:100]}")
		# Don't raise - let server start anyway, embedder will try to load on first request


@app.get("/")
async def root():
	"""Health check endpoint."""
	return {
		"status": "ok",
		"service": "VSS Webhook Server",
		"version": "1.0.0",
	}


@app.post("/webhook", response_model=SubmissionResponse)
async def webhook_submit(data: SubmissionData):
	"""
	Menerima data submission dari Google Form (via Google Apps Script).
	Body JSON: {nama, judul, abstrak, jurusan, tahun}
	Response: {status, id, pesan}
	"""
	try:
		logger.info(f"[Webhook] Menerima submission dari {data.nama}")

		# Validasi input basic
		if not data.judul.strip():
			raise ValueError("Judul tidak boleh kosong")
		if not data.abstrak.strip():
			raise ValueError("Abstrak tidak boleh kosong")

		# Insert dokumen ke ChromaDB
		doc_id, pesan = insert_single_document(
			nama=data.nama,
			judul=data.judul,
			abstrak=data.abstrak,
			jurusan=data.jurusan,
			tahun=data.tahun,
		)

		logger.info(f"[Webhook] Submission berhasil: {doc_id}")
		return SubmissionResponse(
			status="success",
			id=doc_id,
			pesan=pesan,
		)

	except ValueError as exc:
		error_msg = str(exc)
		logger.warning(f"[Webhook] Validation error: {error_msg}")
		raise HTTPException(status_code=400, detail=error_msg)

	except Exception as exc:
		error_msg = f"Internal server error: {str(exc)}"
		logger.error(f"[Webhook] {error_msg}", exc_info=True)
		raise HTTPException(status_code=500, detail=error_msg)


@app.get("/status")
async def get_status():
	"""Endpoint untuk cek jumlah dokumen yang sudah tersimpan."""
	try:
		db = get_database()
		count = db.count()
		logger.info(f"[Webhook] Status check: {count} dokumen di database")
		return {
			"status": "ok",
			"total_documents": count,
		}
	except Exception as exc:
		error_msg = str(exc)
		logger.error(f"[Webhook] Error getting status: {error_msg}", exc_info=True)
		raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
	import uvicorn

	# Jalankan server di localhost:8000
	# Untuk production, expose dengan reverse proxy atau ngrok
	print("[Webhook] Starting VSS Webhook Server...")
	print("[Webhook] Docs tersedia di: http://localhost:8000/docs")
	uvicorn.run(app, host="0.0.0.0", port=8000)