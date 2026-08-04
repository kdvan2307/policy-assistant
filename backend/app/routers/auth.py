from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import User, UserRole
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.utils.security import get_current_user
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.GUEST,  # mặc định Guest — Admin sẽ nâng quyền thủ công (Bước 22)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    # Cố ý dùng chung 1 thông báo lỗi cho cả 2 trường hợp (email sai / password sai)
    # — tránh lộ thông tin "email này có tồn tại hay không" cho kẻ tấn công dò quét.
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email hoặc mật khẩu không đúng.",
    )

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials

    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Route mẫu để test middleware — trả thông tin user đang đăng nhập."""
    return current_user