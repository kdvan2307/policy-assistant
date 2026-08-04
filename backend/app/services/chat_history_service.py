from sqlalchemy.orm import Session

from app.models.models import ChatSession, ChatMessage


def get_or_create_session(db: Session, user_id: int, session_id: int | None) -> ChatSession:
    """Nếu session_id được cung cấp VÀ thuộc đúng user này -> dùng lại.
    Ngược lại (session_id=None, hoặc không tìm thấy/không thuộc user) -> tạo
    session mới. Kiểm tra user_id khớp là bắt buộc — tránh 1 user cố tình
    gửi session_id của người khác để đọc/ghi nhầm lịch sử người đó."""
    if session_id is not None:
        session = db.get(ChatSession, session_id)
        if session is not None and session.user_id == user_id:
            return session

    new_session = ChatSession(user_id=user_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def save_message(
    db: Session, session_id: int, role: str, content: str, sources: list[str] | None = None
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id, role=role, content=content, sources=sources or []
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_sessions(db: Session, user_id: int) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


def get_session_messages(db: Session, session_id: int, user_id: int) -> list[ChatMessage] | None:
    """Trả None nếu session không tồn tại HOẶC không thuộc user này — router
    sẽ tự quyết định trả 404 dựa vào None, không lộ thông tin session của
    người khác dù chỉ là 'session này có tồn tại hay không'."""
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != user_id:
        return None

    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )