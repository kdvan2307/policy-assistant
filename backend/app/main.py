from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.models import models  # noqa: F401
from app.routers import auth, admin, chat
from app.middlewares.logging_middleware import LoggingMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Internal Security Policy Assistant",
    description="Trợ lý AI Tra cứu Chính sách & Quy trình An toàn Thông tin Nội bộ",
    version="0.1.0",
)

# Cho phép frontend (Next.js, cổng 3000) gọi API này. Chỉ khai báo origin cụ
# thể — KHÔNG dùng "*" vì allow_credentials=True không được phép kết hợp
# với wildcard theo chuẩn CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(chat.router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "policy-assistant-backend"}