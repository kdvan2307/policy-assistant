# Schema gửi cho LLM — CHỈ khai báo tham số an toàn (keyword).
# KHÔNG bao giờ thêm "user_role" vào đây, dù có vẻ tiện — xem giải thích
# về rủi ro leo thang đặc quyền ở phần kiến thức nền.
TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Trả về ngày hiện tại theo lịch dương. Dùng khi người dùng hỏi về ngày, thứ, hôm nay.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Tìm kiếm tài liệu chính sách/quy trình an toàn thông tin nội bộ theo từ khóa cụ thể.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Từ khóa cần tìm, ví dụ 'mật khẩu', 'MFA'"}
                },
                "required": ["keyword"],
            },
        },
    },
]