from dataclasses import dataclass

from app.services.embedding_service import _get_model
from app.services.vector_store import search


@dataclass
class RetrievedChunk:
    title: str
    content: str
    document_id: int
    score: float


def retrieve(question: str, user_role: str, top_k: int = 3) -> list[RetrievedChunk]:
    """Pipeline đầy đủ: câu hỏi -> embedding -> tìm kiếm có lọc RBAC -> kết quả.

    Đây là hàm DUY NHẤT mà Bước 12 (API /chat) sẽ gọi tới — mọi logic RBAC
    được đóng gói bên trong, nơi gọi không cần tự viết lại điều kiện lọc.
    """
    # Tiền tố "query: " bắt buộc theo quy ước model e5 (khác "passage: " dùng
    # khi ingest ở Bước 6) — đây là lý do 2 loại text (câu hỏi vs tài liệu)
    # được model học để biểu diễn khác nhau dù cùng 1 không gian vector.
    prefixed_question = f"query: {question}"
    query_embedding = _get_model().encode([prefixed_question], normalize_embeddings=True)[0].tolist()

    raw_results = search(query_embedding, top_k=top_k, user_role=user_role)

    return [
        RetrievedChunk(
            title=r["payload"]["title"],
            content=r["payload"]["content"],
            document_id=r["payload"]["document_id"],
            score=r["score"],
        )
        for r in raw_results
    ]