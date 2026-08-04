from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import User
from app.utils.security import get_current_user
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatSessionResponse, ChatMessageResponse,
)
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.retriever_service import retrieve
from app.services.prompt_builder import build_system_prompt
from app.services.llm_service import generate_answer_with_tools
from app.services.chat_history_service import (
    get_or_create_session, save_message, list_sessions, get_session_messages,
)
from app.services.feedback_service import submit_feedback

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    # ... giữ nguyên toàn bộ nội dung đã có từ Bước 13 ...
    user_role = current_user.role.value
    session = get_or_create_session(db, user_id=current_user.id, session_id=payload.session_id)

    chunks = retrieve(payload.message, user_role=user_role, top_k=3)
    system_prompt = build_system_prompt(chunks)
    answer = generate_answer_with_tools(system_prompt, payload.message, user_role=user_role)
    sources = list(dict.fromkeys(chunk.title for chunk in chunks))

    save_message(db, session.id, role="user", content=payload.message)
    save_message(db, session.id, role="assistant", content=answer, sources=sources)

    return ChatResponse(answer=answer, sources=sources, session_id=session.id)


@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_my_sessions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ChatSessionResponse]:
    return list_sessions(db, user_id=current_user.id)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def get_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessageResponse]:
    messages = get_session_messages(db, session_id=session_id, user_id=current_user.id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện này.")
    return messages


@router.post("/feedback", response_model=FeedbackResponse)
def send_feedback(
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Gửi/cập nhật đánh giá thumbs up/down cho 1 câu trả lời cụ thể."""
    try:
        feedback = submit_feedback(
            db, user_id=current_user.id,
            message_id=payload.message_id, is_helpful=payload.is_helpful,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return FeedbackResponse(
        message_id=feedback.message_id, is_helpful=feedback.is_helpful, created_at=feedback.created_at,
    )