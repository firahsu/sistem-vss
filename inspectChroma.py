import argparse
import json
import sqlite3
from pathlib import Path
 
import chromadb
 
 
def inspect_sqlite_tables(db_path: Path):
    """Lihat daftar tabel mentah di chroma.sqlite3 (opsional, untuk debugging)."""
    if not db_path.exists():
        print(f"  (chroma.sqlite3 tidak ditemukan di {db_path})")
        return
 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  Total tabel: {len(tables)}")
    for t in tables:
        print(f"    - {t}")
    conn.close()
 
 
def inspect_collections(chroma_path: str, sample_size: int = 5):
    client = chromadb.PersistentClient(path=chroma_path)
    collections = client.list_collections()
 
    print("=" * 70)
    print(f"CHROMADB INSPECT REPORT")
    print(f"Path        : {chroma_path}")
    print(f"Total collection: {len(collections)}")
    print("=" * 70)
 
    for col in collections:
        collection = client.get_collection(col.name)
        count = collection.count()
 
        print(f"\n📁 Collection : {col.name}")
        print(f"   UUID       : {col.id}")
        print(f"   Metadata   : {col.metadata}")
        print(f"   Jumlah doc : {count}")
 
        if count == 0:
            print("   (collection kosong, tidak ada data untuk di-sample)")
            continue
 
        # Ambil sample data
        data = collection.get(
            limit=min(sample_size, count),
            include=["metadatas", "documents", "embeddings"],
        )
 
        # Kumpulkan semua unique metadata keys dari sample
        all_keys = set()
        for meta in data.get("metadatas") or []:
            if meta:
                all_keys.update(meta.keys())
 
        print(f"   Field metadata yang ditemukan: {sorted(all_keys) if all_keys else '(tidak ada metadata)'}")
 
        # Info dimensi embedding (kalau ada)
        embeddings = data.get("embeddings")
        if embeddings is not None and len(embeddings) > 0:
            try:
                dim = len(embeddings[0])
                print(f"   Dimensi embedding: {dim}")
            except TypeError:
                pass
 
        print(f"\n   --- Sample {min(sample_size, count)} dokumen ---")
        ids = data.get("ids", [])
        docs = data.get("documents", [])
        metas = data.get("metadatas", [])
 
        for i in range(len(ids)):
            print(f"   [{i}] id       : {ids[i]}")
            doc_preview = (docs[i][:100] + "...") if docs[i] and len(docs[i]) > 100 else docs[i]
            print(f"       document : {doc_preview}")
            print(f"       metadata : {json.dumps(metas[i], ensure_ascii=False)}")
            print()
 
 
def main():
    parser = argparse.ArgumentParser(description="Inspect struktur ChromaDB")
    parser.add_argument(
        "--path", default="./chroma_db", help="Path ke folder chroma_db (default: ./chroma_db)"
    )
    parser.add_argument(
        "--sample", type=int, default=5, help="Jumlah dokumen sample yang ditampilkan per collection"
    )
    parser.add_argument(
        "--raw-tables", action="store_true", help="Tampilkan juga daftar tabel mentah di chroma.sqlite3"
    )
    args = parser.parse_args()
 
    chroma_path = Path(args.path)
    if not chroma_path.exists():
        print(f"❌ Folder '{chroma_path}' tidak ditemukan. Cek lagi --path nya.")
        return
 
    inspect_collections(str(chroma_path), sample_size=args.sample)
 
    if args.raw_tables:
        print("\n" + "=" * 70)
        print("RAW SQLITE TABLES (chroma.sqlite3)")
        print("=" * 70)
        inspect_sqlite_tables(chroma_path / "chroma.sqlite3")
 
 
if __name__ == "__main__":
    main()