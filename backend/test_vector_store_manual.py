import json
from pathlib import Path

from app.services.document_reader import read_document
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embed_chunks
from app.services.vector_store import ensure_collection, upsert_chunk, search

SAMPLE_DIR = Path("sample_documents")
manifest = json.loads((SAMPLE_DIR / "manifest.json").read_text(encoding="utf-8"))

print("Đảm bảo collection tồn tại...")
ensure_collection()

# --- Ingest toàn bộ 6 tài liệu mẫu vào Qdrant ---
for doc_id, doc_meta in enumerate(manifest["documents"], start=1):
    file_path = SAMPLE_DIR / doc_meta["filename"]
    text = read_document(str(file_path), doc_meta["file_type"])
    chunks = chunk_text(text, chunk_size=150, overlap=30)
    embeddings = embed_chunks(chunks)

    for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        upsert_chunk(
            document_id=doc_id,
            chunk_index=chunk_index,
            title=doc_meta["title"],
            content=chunk,
            embedding=embedding,
            allowed_roles=doc_meta["allowed_roles"],
        )
    print(f"Đã insert {len(chunks)} chunk cho: {doc_meta['title']}")

# --- Test tìm kiếm thử ---
print("\n=== Test tìm kiếm: 'mật khẩu cần bao nhiêu ký tự' ===")
from app.services.embedding_service import _get_model

query = "query: mật khẩu cần bao nhiêu ký tự"
query_embedding = _get_model().encode([query], normalize_embeddings=True)[0].tolist()

results = search(query_embedding, top_k=3)
for r in results:
    print(f"[score={r['score']:.3f}] {r['payload']['title']}")
    print(f"  {r['payload']['content'][:100]}...")