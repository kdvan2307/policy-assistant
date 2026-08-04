import json
from pathlib import Path

from app.services.document_reader import read_document
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embed_chunks

SAMPLE_DIR = Path("sample_documents")
manifest = json.loads((SAMPLE_DIR / "manifest.json").read_text(encoding="utf-8"))

for doc_meta in manifest["documents"]:
    file_path = SAMPLE_DIR / doc_meta["filename"]
    print(f"=== {doc_meta['title']} ({doc_meta['file_type']}) ===")

    text = read_document(str(file_path), doc_meta["file_type"])
    print(f"Độ dài text: {len(text)} ký tự")
    print(f"Trích đoạn đầu: {text[:100]!r}")

    chunks = chunk_text(text, chunk_size=150, overlap=30)
    print(f"Số chunk: {len(chunks)}")

    embeddings = embed_chunks(chunks)
    print(f"Chiều vector: {len(embeddings[0])}")
    print()