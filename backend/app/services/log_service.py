from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import RequestLog


def query_logs(
    db: Session,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    endpoint: str | None = None,
    has_error: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[RequestLog]:
    """Truy vấn log có điều kiện — mọi tham số đều TÙY CHỌN (None = không
    lọc theo tiêu chí đó), cho phép Admin kết hợp bất kỳ tổ hợp điều kiện
    nào (chỉ theo thời gian, chỉ theo endpoint, hoặc cả hai cùng lúc...).
    """
    query = db.query(RequestLog)

    if from_date is not None:
        query = query.filter(RequestLog.created_at >= from_date)
    if to_date is not None:
        query = query.filter(RequestLog.created_at <= to_date)
    if endpoint is not None:
        # dùng ILIKE (không phân biệt hoa/thường) + wildcard 2 đầu, để Admin
        # gõ "chat" cũng khớp được "/chat" hoặc "/chat/sessions/1/messages"
        query = query.filter(RequestLog.endpoint.ilike(f"%{endpoint}%"))
    if has_error is True:
        query = query.filter(RequestLog.status_code >= 400)
    elif has_error is False:
        query = query.filter(RequestLog.status_code < 400)

    return (
        query.order_by(RequestLog.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )