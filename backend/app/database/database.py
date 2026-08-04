import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Đọc từ biến môi trường (sẽ dùng khi Docker hóa ở Bước 24) — fallback về
# 1 chuỗi kết nối local mặc định để bạn tự chạy Postgres trên máy khi phát triển.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/policy_assistant",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Lớp cha cho tất cả model."""
    pass


def get_db():
    """Dependency cho FastAPI: mở session, dùng xong tự đóng."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()