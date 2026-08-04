from sqlalchemy.orm import Session

from app.models.models import ChatMessage, Feedback


def submit_feedback(db: Session, user_id: int, message_id: int, is_helpful: bool) -> Feedback:
    """Upsert feedback cho 1 message — tạo mới nếu chưa có, cập nhật nếu đã
    có (người dùng đổi ý). Raise ValueError nếu message không tồn tại hoặc
    không thuộc về user này (chặn IDOR, giống nguyên tắc đã áp dụng ở
    get_session_messages Bước 13)."""
    message = db.get(ChatMessage, message_id)
    if message is None or message.session.user_id != user_id:
        raise ValueError("Không tìm thấy tin nhắn này trong lịch sử của bạn.")

    if message.role != "assistant":
        raise ValueError("Chỉ có thể đánh giá câu trả lời của trợ lý, không thể đánh giá câu hỏi của chính bạn.")

    existing = db.query(Feedback).filter(Feedback.message_id == message_id).first()
    if existing is not None:
        existing.is_helpful = is_helpful
        db.commit()
        db.refresh(existing)
        return existing

    feedback = Feedback(message_id=message_id, is_helpful=is_helpful)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_stats(db: Session) -> dict:
    """Tổng hợp thống kê tỷ lệ hài lòng trên TOÀN HỆ THỐNG — dùng cho
    Admin/Security Manager theo dõi chất lượng trợ lý AI theo thời gian."""
    total = db.query(Feedback).count()
    helpful_count = db.query(Feedback).filter(Feedback.is_helpful.is_(True)).count()
    not_helpful_count = total - helpful_count

    helpful_rate = round((helpful_count / total) * 100, 1) if total > 0 else 0.0

    return {
        "total": total,
        "helpful_count": helpful_count,
        "not_helpful_count": not_helpful_count,
        "helpful_rate": helpful_rate,
    }