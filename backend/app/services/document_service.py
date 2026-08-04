import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.models import Document, DocumentChunk
from app.services.document_reader import read_document
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embed_chunks
from app.services.vector_store import upsert_chunk

ALLOWED_FILE_TYPES = {"md", "pdf", "docx", "html"}
UPLOAD_DIR = Path("uploaded_documents")


def infer_file_type(filename: str) -> str:
    """Suy ra định dạng từ đuôi file — validate ngay tại đây thay vì để lỗi
    xảy ra muộn hơn khi thử đọc file sai định dạng."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_FILE_TYPES:
        raise ValueError(
            f"Định dạng '.{extension}' không được hỗ trợ. "
            f"Chỉ chấp nhận: {', '.join(sorted(ALLOWED_FILE_TYPES))}."
        )
    return extension


def save_uploaded_file(document_id: int, filename: str, content: bytes) -> str:
    """Lưu file vật lý vào thư mục riêng (KHÁC sample_documents/ ở Bước 5,
    vốn chỉ dùng cho dữ liệu mẫu tĩnh) — đặt tên theo document_id để tránh
    trùng lặp nếu 2 Admin cùng upload file có tên giống nhau."""
    UPLOAD_DIR.mkdir(exist_ok=True)
    safe_filename = f"{document_id}_{filename}"
    file_path = UPLOAD_DIR / safe_filename
    file_path.write_bytes(content)
    return str(file_path)


def ingest_document(db: Session, document: Document, file_path: str) -> int:
    """Chạy toàn bộ pipeline Bước 6-7 cho 1 tài liệu duy nhất: đọc -> chia
    chunk -> tạo embedding -> lưu Qdrant -> ghi DocumentChunk vào PostgreSQL.

    Trả về số chunk đã tạo. Raise exception nếu bất kỳ bước nào lỗi — để
    router (nơi gọi hàm này) tự quyết định rollback Document record.
    """
    text = read_document(file_path, document.file_type)
    chunks = chunk_text(text, chunk_size=150, overlap=30)

    if not chunks:
        raise ValueError("Tài liệu không có nội dung để xử lý (file rỗng hoặc không trích được text).")

    embeddings = embed_chunks(chunks)

    for chunk_index, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
        qdrant_point_id = upsert_chunk(
            document_id=document.id,
            chunk_index=chunk_index,
            title=document.title,
            content=chunk_content,
            embedding=embedding,
            allowed_roles=document.allowed_roles,
        )
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=chunk_index,
                content=chunk_content,
                qdrant_point_id=qdrant_point_id,
            )
        )

    db.commit()
    return len(chunks)