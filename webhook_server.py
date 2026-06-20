"""
Webhook Server untuk otomatisasi input data dari Google Form → Google Sheets → Apps Script.
Endpoint POST /webhook menerima data judul skripsi, embedding, dan menyimpannya ke ChromaDB.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

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


class BatchSubmissionData(BaseModel):
	"""Schema untuk batch payload daily sync."""
	documents: list[SubmissionData]


class BatchSubmissionItemResponse(BaseModel):
	"""Schema untuk hasil per dokumen pada batch response."""
	index: int
	status: str
	id: str | None = None
	pesan: str


class BatchSubmissionResponse(BaseModel):
	"""Schema untuk response batch webhook."""
	status: str
	total_received: int
	total_inserted: int
	total_duplicates: int
	total_failed: int
	results: list[BatchSubmissionItemResponse]


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


def _now_iso() -> str:
	return datetime.now().isoformat()


def _clean_text(value: Any) -> str:
	return str(value or "").strip()


def build_data_metadata(
	nama: str,
	judul: str,
	abstrak: str,
	jurusan: str,
	tahun: str,
	source: str,
	status: str,
	created_at: str,
	additional_fields: dict[str, Any] | None = None,
) -> dict:
	metadata = {
		"nama": _clean_text(nama) or "-",
		"judul": _clean_text(judul) or "-",
		"abstrak": _clean_text(abstrak) or "-",
		"jurusan": _clean_text(jurusan) or "-",
		"tahun": _clean_text(tahun) or "-",
		"created_at": created_at,
		"synced_at": created_at,
		"status": status,
		"source": source,
	}
	if additional_fields:
		metadata.update({key: value for key, value in additional_fields.items() if value is not None})
	return metadata


def build_log_metadata(
	nama: str,
	judul: str,
	abstrak: str,
	jurusan: str,
	tahun: str,
	source: str,
	status: str,
	message: str,
	created_at: str,
	doc_id: str,
	related_doc_id: str | None = None,
) -> dict:
	metadata = build_data_metadata(
		nama=nama,
		judul=judul,
		abstrak=abstrak,
		jurusan=jurusan,
		tahun=tahun,
		source=source,
		status=status,
		created_at=created_at,
		additional_fields={
			"record_type": "log",
			"message": message,
			"attempt_doc_id": doc_id,
			"related_doc_id": related_doc_id,
		},
	)
	metadata["record_type"] = "log"
	return metadata


def store_sync_log(
	db: VectorDatabase,
	doc_id: str,
	nama: str,
	judul: str,
	abstrak: str,
	jurusan: str,
	tahun: str,
	source: str,
	status: str,
	message: str,
	related_doc_id: str | None = None,
	created_at: str | None = None,
) -> str:
	log_id = f"log_{doc_id}"
	timestamp = created_at or _now_iso()
	metadata = build_log_metadata(
		nama=nama,
		judul=judul,
		abstrak=abstrak,
		jurusan=jurusan,
		tahun=tahun,
		source=source,
		status=status,
		message=message,
		created_at=timestamp,
		doc_id=doc_id,
		related_doc_id=related_doc_id,
	)
	db.insert_log(log_id, metadata)
	return log_id


# ============================================================================
# Helper: Insert single document
# ============================================================================
def insert_single_document(
	nama: str,
	judul: str,
	abstrak: str,
	jurusan: str,
	tahun: str,
	source: str = "form_submit",
) -> tuple[str, str, str]:
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
		tuple (doc_id, pesan_status, status)

	Raises:
		Exception: Jika terjadi error saat embedding atau insert
	"""
	# Generate unique document ID dengan timestamp + UUID
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	unique_id = str(uuid.uuid4())[:8]
	doc_id = f"doc_{timestamp}_{unique_id}"
	now_iso = _now_iso()
	db = get_database()

	try:
		duplicate, existing_id = db.check_duplicate(judul, nama, tahun)
		if duplicate:
			message = f"Dokumen sudah ada di database (id: {existing_id})"
			store_sync_log(
				db=db,
				doc_id=doc_id,
				nama=nama,
				judul=judul,
				abstrak=abstrak,
				jurusan=jurusan,
				tahun=tahun,
				source=source,
				status="duplicate",
				message=message,
				related_doc_id=existing_id,
				created_at=now_iso,
			)
			return existing_id or doc_id, message, "duplicate"

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
		metadata = build_data_metadata(
			nama=nama,
			judul=judul,
			abstrak=abstrak,
			jurusan=jurusan,
			tahun=tahun,
			source=source,
			status="success",
			created_at=now_iso,
		)

		# Step 4: Insert ke ChromaDB
		db.insert(doc_id, embedding, metadata)
		store_sync_log(
			db=db,
			doc_id=doc_id,
			nama=nama,
			judul=judul,
			abstrak=abstrak,
			jurusan=jurusan,
			tahun=tahun,
			source=source,
			status="success",
			message=f"Dokumen '{judul[:50]}...' berhasil disimpan ke ChromaDB",
			related_doc_id=doc_id,
			created_at=now_iso,
		)
		logger.info(f"[Webhook] Dokumen berhasil disimpan: {doc_id}")

		return doc_id, f"Dokumen '{judul[:50]}...' berhasil disimpan ke ChromaDB", "success"

	except Exception as exc:
		error_msg = f"Error processing {doc_id}: {str(exc)}"
		try:
			store_sync_log(
				db=db,
				doc_id=doc_id,
				nama=nama,
				judul=judul,
				abstrak=abstrak,
				jurusan=jurusan,
				tahun=tahun,
				source=source,
				status="failed",
				message=error_msg,
				created_at=now_iso,
			)
		except Exception:
			logger.warning(f"[Webhook] Gagal menyimpan log untuk {doc_id}", exc_info=True)
		logger.error(f"[Webhook] {error_msg}", exc_info=True)
		raise


def process_batch_documents(
	documents: list[SubmissionData],
	source: str,
) -> BatchSubmissionResponse:
	db = get_database()
	results: list[BatchSubmissionItemResponse] = []
	pending_items: list[dict[str, Any]] = []
	inserted_count = 0
	duplicate_count = 0
	failed_count = 0

	for index, data in enumerate(documents, start=1):
		created_at = _now_iso()
		doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

		try:
			if not data.judul.strip():
				raise ValueError("Judul tidak boleh kosong")
			if not data.abstrak.strip():
				raise ValueError("Abstrak tidak boleh kosong")

			duplicate, existing_id = db.check_duplicate(data.judul, data.nama, data.tahun)
			if duplicate:
				duplicate_count += 1
				message = f"Duplikat, sudah ada di database (id: {existing_id})"
				store_sync_log(
					db=db,
					doc_id=doc_id,
					nama=data.nama,
					judul=data.judul,
					abstrak=data.abstrak,
					jurusan=data.jurusan,
					tahun=data.tahun,
					source=source,
					status="duplicate",
					message=message,
					related_doc_id=existing_id,
					created_at=created_at,
				)
				results.append(
					BatchSubmissionItemResponse(
						index=index,
						status="duplicate",
						id=existing_id,
						pesan=message,
					)
				)
				continue

			combined_text = combine_title_abstract(data.judul, data.abstrak)
			metadata = build_data_metadata(
				nama=data.nama,
				judul=data.judul,
				abstrak=data.abstrak,
				jurusan=data.jurusan,
				tahun=data.tahun,
				source=source,
				status="success",
				created_at=created_at,
			)
			pending_items.append(
				{
					"index": index,
					"doc_id": doc_id,
					"data": data,
					"combined_text": combined_text,
					"metadata": metadata,
					"created_at": created_at,
				}
			)
		except Exception as exc:
			failed_count += 1
			error_message = str(exc)
			store_sync_log(
				db=db,
				doc_id=doc_id,
				nama=data.nama,
				judul=data.judul,
				abstrak=data.abstrak,
				jurusan=data.jurusan,
				tahun=data.tahun,
				source=source,
				status="failed",
				message=error_message,
				created_at=created_at,
			)
			results.append(
				BatchSubmissionItemResponse(
					index=index,
					status="failed",
					id=None,
					pesan=error_message,
				)
			)

	if pending_items:
		try:
			embedder = get_embedder()
			logger.info(f"[Webhook] Batch embedding {len(pending_items)} dokumen...")
			texts = [item["combined_text"] for item in pending_items]
			embeddings = embedder.embed_batch(texts, batch_size=32)
			doc_ids = [item["doc_id"] for item in pending_items]
			metadatas = [item["metadata"] for item in pending_items]

			db.insert_batch(doc_ids, embeddings, metadatas)

			for item in pending_items:
				inserted_count += 1
				data = item["data"]
				store_sync_log(
					db=db,
					doc_id=item["doc_id"],
					nama=data.nama,
					judul=data.judul,
					abstrak=data.abstrak,
					jurusan=data.jurusan,
					tahun=data.tahun,
					source=source,
					status="success",
					message=f"Dokumen '{data.judul[:50]}...' berhasil disimpan ke ChromaDB",
					related_doc_id=item["doc_id"],
					created_at=item["created_at"],
				)
				results.append(
					BatchSubmissionItemResponse(
						index=item["index"],
						status="success",
						id=item["doc_id"],
						pesan=f"Dokumen '{data.judul[:50]}...' berhasil disimpan ke ChromaDB",
					)
				)
		except Exception as exc:
			logger.error(f"[Webhook] Batch insert error: {str(exc)}", exc_info=True)
			for item in pending_items:
				failed_count += 1
				data = item["data"]
				store_sync_log(
					db=db,
					doc_id=item["doc_id"],
					nama=data.nama,
					judul=data.judul,
					abstrak=data.abstrak,
					jurusan=data.jurusan,
					tahun=data.tahun,
					source=source,
					status="failed",
					message=f"Batch insert gagal: {str(exc)}",
					created_at=item["created_at"],
				)
				results.append(
					BatchSubmissionItemResponse(
						index=item["index"],
						status="failed",
						id=None,
						pesan=f"Batch insert gagal: {str(exc)}",
					)
				)

	total_received = len(documents)
	response_status = "success"
	if failed_count > 0:
		response_status = "partial_success" if inserted_count > 0 or duplicate_count > 0 else "failed"
	elif duplicate_count > 0:
		response_status = "success_with_duplicates"

	results.sort(key=lambda item: item.index)
	return BatchSubmissionResponse(
		status=response_status,
		total_received=total_received,
		total_inserted=inserted_count,
		total_duplicates=duplicate_count,
		total_failed=failed_count,
		results=results,
	)


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
		doc_id, pesan, status = insert_single_document(
			nama=data.nama,
			judul=data.judul,
			abstrak=data.abstrak,
			jurusan=data.jurusan,
			tahun=data.tahun,
			source="form_submit",
		)

		logger.info(f"[Webhook] Submission selesai: {doc_id} ({status})")
		return SubmissionResponse(
			status=status,
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


@app.post("/webhook/batch", response_model=BatchSubmissionResponse)
async def webhook_batch(data: BatchSubmissionData):
	"""Menerima batch submission untuk daily sync dari Apps Script."""
	try:
		logger.info(f"[Webhook] Menerima batch submission: {len(data.documents)} dokumen")
		response = process_batch_documents(data.documents, source="daily_sync")
		logger.info(
			"[Webhook] Batch selesai: "
			f"inserted={response.total_inserted}, duplicates={response.total_duplicates}, failed={response.total_failed}"
		)
		return response
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
		stats = db.get_sync_stats()
		logger.info(f"[Webhook] Status check: {count} dokumen di database")
		return {
			"status": "ok",
			"total_documents": count,
			"sync_stats": stats,
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