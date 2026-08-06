# Trợ lý AI Tra cứu Chính sách & Quy trình An toàn Thông tin Nội bộ

Hệ thống RAG (Retrieval-Augmented Generation) có RBAC, cho phép nhân viên
tra cứu chính sách/quy trình ATTT nội bộ qua giao diện chat, với AI trả lời
dựa trên tài liệu thật và tự động lọc theo quyền truy cập từng vai trò.

## Tính năng chính

- Đăng nhập, phân quyền theo 4 vai trò: Admin, Security Manager, Employee, Guest
- Tra cứu tài liệu bằng ngôn ngữ tự nhiên (RAG), trả lời kèm trích dẫn nguồn
- Lọc tài liệu theo quyền truy cập ngay trong lúc tìm kiếm (không lộ tài liệu ngoài quyền)
- Admin upload tài liệu mới (md/pdf/docx/html), tự động tạo chỉ mục tìm kiếm
- Lưu lịch sử hội thoại theo phiên, cho phép đánh giá thumbs up/down từng câu trả lời
- Admin xem log truy cập hệ thống, thống kê tỷ lệ hài lòng người dùng

## Kiến trúc tổng quan
                 +----------------------+
                 |  Frontend (Next.js)  |
                 +----------+-----------+
                            |
                       HTTP/REST API
                            |
                            v
                 +----------------------+
                 |  Backend (FastAPI)   |
                 |                      |
                 |  - Authentication    |
                 |  - RBAC              |
                 |  - Chat API          |
                 |  - Admin API         |
                 |  - RAG Pipeline      |
                 +-----+-----------+----+
                       |           |
             SQLAlchemy|           | Vector Search
                       |           |
                       v           v
              +---------------+  +----------------+
              | PostgreSQL    |  | Qdrant         |
              |               |  | Vector Database|
              | User          |  +--------+-------+
              | Session       |           |
              | Chat Log      |           |
              | Documents     |           |
              +---------------+           |
                                          |
                                          v
                              +-----------------------+
                              | Ollama               |
                              | Qwen2.5-3B-Instruct  |
                              | (Host Machine)       |
                              +-----------------------+

## Yêu cầu hệ thống

- Docker + Docker Compose
- [Ollama](https://ollama.com) cài trên máy host (KHÔNG chạy trong Docker)
- GPU NVIDIA khuyến nghị (tối thiểu 4GB VRAM) để chạy LLM local mượt hơn

## Cài đặt & chạy — Cách 1: Docker (khuyến nghị)

**Bước 1 — Chuẩn bị Ollama trên máy host (bắt buộc làm TRƯỚC khi chạy Docker):**
```bash
ollama pull qwen2.5:3b-instruct
```

**Bước 2 — Khởi động toàn bộ hệ thống:**
```bash
docker-compose up --build
```

**Bước 3 — Truy cập:**
- Frontend: http://localhost:3000
- Backend API docs (Swagger): http://localhost:8000/docs
- Qdrant dashboard: http://localhost:6333/dashboard

**Lưu ý:** lần đầu chạy, database trống hoàn toàn — cần tự đăng ký tài khoản
qua `/auth/register`, sau đó tự nâng quyền Admin cho tài khoản đầu tiên bằng SQL:
```bash
docker exec -it policy-assistant-postgres-1 psql -U postgres -d policy_assistant \
  -c "UPDATE users SET role = 'admin' WHERE email = 'ban@company.com';"
```
Sau khi có tài khoản Admin, các tài khoản/quyền tiếp theo có thể quản lý qua
giao diện Admin (`/admin` sau khi đăng nhập bằng tài khoản admin).

## Cài đặt & chạy — Cách 2: Thủ công (không dùng Docker)

**PostgreSQL & Qdrant** (chạy nhanh qua Docker, không cần cài native):
```bash
docker run --name policy-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=policy_assistant -p 5432:5432 -d postgres:16
docker run --name policy-qdrant -p 6333:6333 -d qdrant/qdrant:v1.11.0
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash; venv\Scripts\activate cho CMD
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend** (terminal khác):
```bash
cd frontend
npm install
npm run dev
```

## Cấu trúc thư mục
backend/
├── app/
│ ├── routers/ # API endpoints: auth, admin, chat
│ ├── services/ # Toàn bộ logic nghiệp vụ — xem README_rag.md,
│ │ # README_auth.md, README_chat_tools.md
│ ├── middlewares/ # Logging middleware
│ ├── models/ # SQLAlchemy models (PostgreSQL)
│ ├── schemas/ # Pydantic schemas (request/response API)
│ └── database/ # Kết nối PostgreSQL
├── sample_documents/ # 6 tài liệu mẫu (Bước 5) — dữ liệu demo, ingest thủ công
├── uploaded_documents/ # Tài liệu do Admin upload qua UI (runtime, có volume Docker)
├── tests/ # Unit test (pytest)
frontend/
├── src/
│ ├── app/ # Route theo App Router: /login, /chat, /admin
│ ├── components/ # UI: ChatWindow, FeedbackButtons, admin/*
│ └── services/ # api.js (gọi backend), auth.js (quản lý token)
## Chạy test

```bash
cd backend
pytest tests/ -v
```

CI tự động chạy test này mỗi lần push (xem `.github/workflows/backend-tests.yml`).

## Ghi chú quan trọng

- Model LLM (Qwen2.5-3B-Instruct, chạy qua Ollama) **không nằm trong Docker Compose** — phải cài và chạy sẵn trên máy host trước, backend gọi qua `host.docker.internal:11434`.
- 6 tài liệu mẫu trong `sample_documents/` KHÔNG tự động ingest khi khởi động hệ thống lần đầu — cần tự ingest qua trang Admin (upload từng file), hoặc chạy tay script ingest (xem README_rag.md).
- Chỉ sử dụng dữ liệu chính sách thật của tổ chức khi triển khai thực tế — dữ liệu mẫu trong repo chỉ phục vụ demo/học tập.