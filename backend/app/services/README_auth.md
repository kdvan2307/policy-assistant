# Authentication & RBAC

Nhóm module chịu trách nhiệm: xác thực người dùng (đăng nhập, JWT) và phân
quyền theo 4 vai trò (Admin, Security Manager, Employee, Guest).

## Các file

| File | Vai trò |
|---|---|
| `auth_service.py` | Hash/verify password (bcrypt), sinh/giải mã JWT token |
| `../utils/security.py` | `get_current_user` (xác thực), `require_role` (chặn route theo vai trò), `can_access_document` (kiểm tra quyền từng bản ghi) |
| `user_service.py` | Quản lý danh sách user, đổi role (dành cho trang Admin) |

## 2 tầng RBAC trong hệ thống — dễ nhầm lẫn

1. **Route-level** (`require_role`): chặn nguyên 1 API endpoint theo vai trò.
   Dùng ở: `/admin/*` (chỉ Admin), `/admin/feedback-stats` (Admin + Security Manager).
2. **Data-level** (lọc trong `vector_store.search`, xem README_rag.md): cùng
   1 route `/chat` cho MỌI vai trò gọi được, nhưng dữ liệu trả về khác nhau
   tùy vai trò người hỏi.

## Quy tắc bảo mật quan trọng đã áp dụng

- **Admin không thể tự đổi role của chính mình** (`user_service.update_user_role`)
  — tránh khóa quyền quản trị vĩnh viễn nếu chỉ có 1 tài khoản Admin.
- **`role` không bao giờ nhận từ client** — luôn lấy từ `current_user` (suy ra
  từ JWT đã xác thực), không đọc từ request body — tránh leo thang đặc quyền.
- **Kiểm tra quyền sở hữu (chống IDOR)** khi truy cập session/message/feedback
  — user A không thể đọc/ghi dữ liệu của user B dù đoán đúng ID (xem
  `chat_history_service.get_session_messages`, `feedback_service.submit_feedback`).

## Tài khoản Admin đầu tiên

Hệ thống không có sẵn tài khoản Admin — phải tự đăng ký qua `/auth/register`
rồi nâng quyền bằng SQL trực tiếp (xem README tổng, mục Cài đặt). Các Admin
sau đó có thể phân quyền tiếp qua giao diện `/admin`.