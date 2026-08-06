# RAG Pipeline — Retrieval-Augmented Generation

Nhóm module chịu trách nhiệm: đọc tài liệu, chia nhỏ, tạo vector embedding,
lưu trữ tìm kiếm, và truy xuất có lọc quyền truy cập (RBAC).

## Các file

| File | Vai trò |
|---|---|
| `document_reader.py` | Đọc nội dung text thuần từ 4 định dạng: md, pdf, docx, html |
| `chunk_service.py` | Chia văn bản dài thành đoạn nhỏ (chunk), có overlap giữa các đoạn |
| `embedding_service.py` | Tạo vector embedding bằng model `multilingual-e5-small` (chạy CPU, không tranh VRAM với LLM) |
| `vector_store.py` | Kết nối Qdrant — lưu (upsert) và tìm kiếm (search) vector, có áp Filter theo `allowed_roles` |
| `retriever_service.py` | Pipeline hoàn chỉnh: câu hỏi → embedding → tìm kiếm có lọc RBAC → kết quả |
| `document_service.py` | Điều phối ingest tài liệu mới: đọc → chunk → embedding → lưu Qdrant + PostgreSQL |

## Luồng ingest 1 tài liệu
File (md/pdf/docx/html)
→ document_reader.read_document() # ra text thuần
→ chunk_service.chunk_text() # ra list[str], mỗi đoạn ~150 từ
→ embedding_service.embed_chunks() # ra list[vector 384 chiều]
→ vector_store.upsert_chunk() # lưu vào Qdrant, kèm allowed_roles
→ ghi DocumentChunk vào PostgreSQL # lưu con trỏ qdrant_point_id
## Luồng truy vấn (mỗi lần chat)
Câu hỏi + role người dùng
→ retriever_service.retrieve()
→ embedding câu hỏi (tiền tố BẮT BUỘC "query: ", khác "passage: " lúc ingest)
→ vector_store.search() — CHỈ trả chunk có allowed_roles chứa đúng role
→ list[RetrievedChunk]
## Điểm cần biết khi sửa/mở rộng

- **Model embedding chạy CPU có chủ đích** — không đổi sang GPU nếu chưa cân nhắc kỹ, vì Ollama (LLM) đã dùng phần lớn VRAM sẵn có.
- **Tiền tố `"query: "` / `"passage: "` không được bỏ** — đây là quy ước bắt buộc của model `e5`, thiếu tiền tố làm giảm chất lượng tìm kiếm đáng kể (đã debug thực tế ở quá trình xây dựng, xem lịch sử Bước 11).
- **RBAC filter nằm ở `vector_store.search()`**, không phải ở `retriever_service.py` — nếu cần sửa logic phân quyền tìm kiếm, sửa đúng file này. Có unit test bảo vệ hành vi này ở `tests/test_vector_store.py`.
- **6 tài liệu mẫu (`sample_documents/`) không có `Document` record thật trong PostgreSQL** — chỉ ingest thẳng vào Qdrant lúc setup ban đầu, khác với tài liệu upload qua UI (có đủ record cả 2 nơi).