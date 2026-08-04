from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load — chỉ tải model vào bộ nhớ lần đầu được gọi, không tải
    ngay lúc import (tránh làm chậm khởi động app nếu chưa cần dùng ngay)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")
    return _model


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Sinh vector embedding cho danh sách chunk text.

    Model e5 yêu cầu tiền tố 'passage: ' cho văn bản lưu trữ (khác 'query: '
    dùng cho câu hỏi tìm kiếm ở Bước 8) — quy ước riêng của model, bỏ qua sẽ
    làm giảm chất lượng tìm kiếm.
    """
    model = _get_model()
    prefixed = [f"passage: {chunk}" for chunk in chunks]
    embeddings = model.encode(prefixed, normalize_embeddings=True)
    return embeddings.tolist()