from sqlalchemy.orm import Session

from app.models.models import User, UserRole


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def update_user_role(db: Session, target_user_id: int, new_role: str, current_user_id: int) -> User:
    """Đổi role của 1 user. Raise ValueError nếu:
    - user không tồn tại
    - role mới không hợp lệ
    - Admin cố tự đổi role của CHÍNH MÌNH (phòng khóa quyền quản trị vĩnh viễn)
    """
    if target_user_id == current_user_id:
        raise ValueError("Không thể tự thay đổi role của chính tài khoản đang đăng nhập.")

    valid_roles = {r.value for r in UserRole}
    if new_role not in valid_roles:
        raise ValueError(f"Role không hợp lệ. Chỉ chấp nhận: {sorted(valid_roles)}.")

    user = db.get(User, target_user_id)
    if user is None:
        raise ValueError("Không tìm thấy người dùng này.")

    user.role = UserRole(new_role)
    db.commit()
    db.refresh(user)
    return user