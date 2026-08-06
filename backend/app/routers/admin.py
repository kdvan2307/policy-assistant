from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.database import get_db
from app.models.models import User, UserRole, Document
from app.utils.security import require_role
from app.schemas.document import DocumentUploadResponse, DocumentListResponse
from app.schemas.log import RequestLogResponse
from app.schemas.user import UserListResponse, UpdateRoleRequest
from app.schemas.feedback import FeedbackStatsResponse
from app.services.document_service import (
    infer_file_type, save_uploaded_file, ingest_document, list_documents,
)
from app.services.vector_store import ensure_collection
from app.services.log_service import query_logs
from app.services.user_service import list_users, update_user_role
from app.services.feedback_service import get_feedback_stats

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
def admin_ping(current_user: User = Depends(require_role(UserRole.ADMIN))) -> dict:
    return {"message": f"Xin chào Admin {current_user.email}", "role": current_user.role.value}


@router.get("/security-ping")
def security_ping(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SECURITY_MANAGER))
) -> dict:
    return {"message": f"Xin chào {current_user.email}", "role": current_user.role.value}


@router.post("/documents", response_model=DocumentUploadResponse)
def upload_document(
    title: str = Form(...),
    allowed_roles: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    try:
        file_type = infer_file_type(file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    role_list = [r.strip() for r in allowed_roles.split(",") if r.strip()]
    valid_role_values = {r.value for r in UserRole}
    invalid_roles = [r for r in role_list if r not in valid_role_values]
    if invalid_roles:
        raise HTTPException(status_code=400, detail=f"Role không hợp lệ: {invalid_roles}.")
    if not role_list:
        raise HTTPException(status_code=400, detail="Phải chỉ định ít nhất 1 role.")

    document = Document(title=title, file_type=file_type, allowed_roles=role_list, uploaded_by=current_user.id)
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        content = file.file.read()
        file_path = save_uploaded_file(document.id, file.filename, content)
        ensure_collection()
        chunks_created = ingest_document(db, document, file_path)
    except Exception as exc:
        db.delete(document)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Lỗi khi xử lý tài liệu: {exc}")

    return DocumentUploadResponse(
        id=document.id, title=document.title, file_type=document.file_type,
        allowed_roles=document.allowed_roles, chunks_created=chunks_created,
    )


@router.get("/documents", response_model=list[DocumentListResponse])
def get_documents(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[DocumentListResponse]:
    """Danh sách toàn bộ tài liệu đã upload qua API (Bước 14) — LƯU Ý: 6 tài
    liệu mẫu ingest thủ công ở Bước 5-8 không có Document record thật trong
    PostgreSQL, nên sẽ KHÔNG xuất hiện ở đây (đã ghi chú khi debug Bước 14)."""
    return list_documents(db)


@router.get("/logs", response_model=list[RequestLogResponse])
def get_logs(
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    endpoint: str | None = Query(None),
    has_error: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[RequestLogResponse]:
    return query_logs(db, from_date=from_date, to_date=to_date, endpoint=endpoint, has_error=has_error, limit=limit, offset=offset)


@router.get("/feedback-stats", response_model=FeedbackStatsResponse)
def feedback_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SECURITY_MANAGER)),
    db: Session = Depends(get_db),
) -> FeedbackStatsResponse:
    return FeedbackStatsResponse(**get_feedback_stats(db))


@router.get("/users", response_model=list[UserListResponse])
def get_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserListResponse]:
    return list_users(db)


@router.patch("/users/{user_id}/role", response_model=UserListResponse)
def change_user_role(
    user_id: int,
    payload: UpdateRoleRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserListResponse:
    try:
        updated_user = update_user_role(db, target_user_id=user_id, new_role=payload.role, current_user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_user