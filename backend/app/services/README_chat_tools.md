# Chat & Tool-Calling

Nhóm module chịu trách nhiệm: gọi LLM (Ollama), xây system prompt ép model
bám sát tài liệu, và cơ chế tool-calling cho phép model tự gọi thêm công cụ
khi cần (không phải lúc nào cũng chỉ dựa vào RAG tự động).

## Các file

| File | Vai trò |
|---|---|
| `llm_service.py` | Gọi Ollama (model `qwen2.5:3b-instruct`); có 2 hàm: `generate_answer` (đơn giản) và `generate_answer_with_tools` (cho phép model tự gọi tool) |
| `prompt_builder.py` | Xây system prompt: ép model chỉ dùng context được cấp, từ chối khi không có data, luôn trích nguồn |
| `tool_manager.py` | Registry (dict tra cứu, không if/elif) ánh xạ tên tool → hàm thực thi thật |
| `tools/date_tool.py`, `tools/policy_search_tool.py` | 2 tool: lấy ngày hiện tại, tìm kiếm tài liệu theo từ khóa |
| `tools/tool_specs.py` | Schema tool gửi cho LLM — CHỈ chứa tham số an toàn, không bao giờ có `user_role` |

## Nguyên tắc bảo mật quan trọng nhất của nhóm này

`user_role` dùng để lọc RBAC khi tool `search_policy` chạy **luôn được backend
tự tiêm vào** (`tool_manager.execute_tool(name, args, user_role)`), **không
bao giờ** để LLM tự cung cấp tham số này qua `arguments` do model sinh ra —
tránh 1 dạng tấn công leo thang đặc quyền qua prompt injection (ví dụ người
dùng cố tình hỏi "tra cứu với quyền admin giúp tôi").

## Bài học kỹ thuật đáng lưu ý (rút ra trong quá trình xây dựng)

Kết quả tìm kiếm trả về cho tool từng bị cắt ngắn cứng (`content[:200]`),
vô tình xén mất đúng đoạn thông tin cần thiết nằm ở giữa/cuối chunk (case
thực tế: hỏi về MFA nhưng bị cắt trước khi tới đoạn nói về MFA). Đã sửa bằng
cách trả nguyên vẹn nội dung chunk cho tool — xem lịch sử debug ở
`policy_search_tool.py` nếu cần tham khảo cách chẩn đoán loại lỗi này.

## Model đang dùng

`qwen2.5:3b-instruct` qua Ollama — chạy trên máy host, biến môi trường
`OLLAMA_HOST` cần trỏ `host.docker.internal:11434` khi chạy qua Docker.