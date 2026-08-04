import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.database.database import SessionLocal
from app.models.models import RequestLog
from app.services.auth_service import decode_access_token


class LoggingMiddleware(BaseHTTPMiddleware):
    """Ghi log MỌI request đi qua — endpoint, thời gian phản hồi, mã trạng
    thái, lỗi nếu có. Tự mở DB session riêng (không dùng Depends(get_db))
    vì middleware chạy NGOÀI vòng đời dependency injection của từng route.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        status_code = 500  # giá trị mặc định nếu route crash hoàn toàn, không kịp trả response
        error_message = None
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            error_message = str(exc)
            raise  # ném lại lỗi để FastAPI xử lý bình thường (trả 500 cho client)
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self._save_log(request, status_code, duration_ms, error_message)

        return response

    def _save_log(self, request: Request, status_code: int, duration_ms: float, error_message: str | None) -> None:
        """Ghi 1 dòng log vào DB. Bọc try/except RIÊNG cho việc ghi log —
        nếu chính DB logging bị lỗi (ví dụ Postgres tạm mất kết nối), TUYỆT
        ĐỐI không được làm sập luôn cả request gốc chỉ vì không ghi log được."""
        db = SessionLocal()
        try:
            log_entry = RequestLog(
                method=request.method,
                endpoint=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
                error_message=error_message,
                user_id=self._try_extract_user_id(request),
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            db.rollback()  # log lỗi ghi log ra console, không raise tiếp
        finally:
            db.close()

    def _try_extract_user_id(self, request: Request) -> int | None:
        """Cố gắng lấy user_id từ token trong header, nếu có. Trả None nếu
        không có token/token không hợp lệ (ví dụ request tới /health, hoặc
        request đăng nhập thất bại) — log vẫn được ghi, chỉ thiếu user_id."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ")
        payload = decode_access_token(token)
        if payload is None:
            return None

        user_id = payload.get("sub")
        return int(user_id) if user_id else None