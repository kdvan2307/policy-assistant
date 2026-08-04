from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import User, UserRole, Document
from app.services.auth_service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực. Vui lòng đăng nhập lại.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_error

    return user


def require_role(*allowed_roles: UserRole):
    """Dependency factory — trả về 1 dependency chỉ cho phép các role được
    liệt kê trong allowed_roles. Dùng ở route:
        Depends(require_role(UserRole.ADMIN))
        Depends(require_role(UserRole.ADMIN, UserRole.SECURITY_MANAGER))
    """

    def _check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu quyền: {', '.join(r.value for r in allowed_roles)}. "
                       f"Role hiện tại: {current_user.role.value}.",
            )
        return current_user

    return _check_role


def can_access_document(user: User, document: Document) -> bool:
    """Kiểm tra quyền ở TẦNG DỮ LIỆU — dùng khi lọc tài liệu/chunk theo role,
    khác với require_role (chặn nguyên 1 route). Sẽ dùng ở Bước 8 (retriever RBAC).

    Admin luôn được xem mọi tài liệu, bất kể allowed_roles ghi gì — vai trò
    quản trị cao nhất không nên bị giới hạn bởi dữ liệu cấu hình có thể sai sót.
    """
    if user.role == UserRole.ADMIN:
        return True
    return user.role.value in document.allowed_roles