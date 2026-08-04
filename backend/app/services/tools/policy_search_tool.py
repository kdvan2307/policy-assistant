from app.services.retriever_service import retrieve


def search_policy(keyword: str, user_role: str) -> dict:
    """Tìm tài liệu chính sách theo từ khóa, CÓ lọc RBAC. top_k=5 để lấy đủ
    rộng, KHÔNG cắt ngắn nội dung chunk trả về — cắt cứng theo ký tự đã từng
    làm mất đúng phần thông tin cần thiết nằm ở giữa/cuối chunk (bài học rút
    ra khi debug case MFA)."""
    chunks = retrieve(keyword, user_role=user_role, top_k=5)
    if not chunks:
        return {"results": [], "note": "Không tìm thấy tài liệu phù hợp trong phạm vi quyền truy cập."}

    return {
        "results": [
            {"title": c.title, "excerpt": c.content, "score": round(c.score, 3)}
            for c in chunks
        ]
    }