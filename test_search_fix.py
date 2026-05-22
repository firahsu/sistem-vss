#!/usr/bin/env python3
"""Test script to verify search functionality with field mapping fix"""

from modules.searcher import Searcher

print("=" * 60)
print("Testing Search Functionality with Field Mapping Fix")
print("=" * 60)

try:
    searcher = Searcher()
    print(f"\n✓ Searcher initialized successfully")
    print(f"✓ Total documents in database: {searcher.db.count()}")
    
    # Test search
    search_query = "deteksi kemiripan"
    print(f"\nSearching for: '{search_query}'")
    print("-" * 60)
    
    results = searcher.search(search_query, top_n=3)
    
    if results:
        print(f"✓ Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Judul: {result['judul'][:70]}")
            print(f"   Mahasiswa: {result['mahasiswa']}")
            print(f"   Jurusan/Prodi: {result['prodi']}")
            print(f"   Tahun: {result['tahun']}")
            print(f"   Similarity: {result['similarity']*100:.2f}%")
            print()
    else:
        print("✗ No results found")
        
    print("=" * 60)
    print("Test complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
