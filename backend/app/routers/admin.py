from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from app.services.feedback_service import get_feedback_stats
from app.schemas.feedback import FeedbackStatsResponse
from app.database.database import get_db
from app.models.models import User, UserRole, Document
from app.utils.security import require_role
from app.schemas.document import DocumentUploadResponse
from app.schemas.log import RequestLogResponse
from app.services.document_service import (
    infer_file_type, save_uploaded_file, ingest_document,
)
from app.services.vector_store import ensure_collection
from app.services.log_service import query_logs

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
    # ... giữ nguyên toàn bộ nội dung đã có từ Bước 14 ...
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


@router.get("/logs", response_model=list[RequestLogResponse])
def get_logs(
    from_date: datetime | None = Query(None, description="Lọc log từ thời điểm này (ISO format, vd: 2026-08-01T00:00:00)"),
    to_date: datetime | None = Query(None, description="Lọc log tới thời điểm này"),
    endpoint: str | None = Query(None, description="Lọc theo endpoint, khớp gần đúng (vd: 'chat')"),
    has_error: bool | None = Query(None, description="true = chỉ log lỗi (status >= 400), false = chỉ log thành công"),
    limit: int = Query(50, ge=1, le=200, description="Số dòng tối đa mỗi lần gọi"),
    offset: int = Query(0, ge=0, description="Bỏ qua bao nhiêu dòng đầu — dùng để phân trang"),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[RequestLogResponse]:
    """Chỉ Admin xem được log hệ thống — Security Manager KHÔNG có quyền
    này (khác /admin/security-ping ở Bước 4), vì log request có thể chứa
    thông tin nhạy cảm về hành vi của mọi user, kể cả Security Manager khác."""
    return query_logs(
        db, from_date=from_date, to_date=to_date, endpoint=endpoint,
        has_error=has_error, limit=limit, offset=offset,
    )
    
@router.get("/feedback-stats", response_model=FeedbackStatsResponse)
def feedback_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SECURITY_MANAGER)),
    db: Session = Depends(get_db),
) -> FeedbackStatsResponse:
    """Thống kê tổng thể — cho phép CẢ Admin lẫn Security Manager xem (khác
    /admin/logs chỉ Admin), vì đây là chỉ số CHẤT LƯỢNG dịch vụ, không phải
    dữ liệu giám sát hành vi người dùng nhạy cảm như log request."""
    stats = get_feedback_stats(db)
    return FeedbackStatsResponse(**stats)