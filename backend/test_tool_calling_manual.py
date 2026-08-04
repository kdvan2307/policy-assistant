from app.services.llm_service import generate_answer_with_tools

SYSTEM_PROMPT = """Bạn là trợ lý AI tra cứu chính sách an toàn thông tin nội bộ.
Bạn có thể dùng tool get_current_date khi được hỏi về ngày tháng, hoặc
search_policy khi cần tìm thêm thông tin trong tài liệu nội bộ."""

TEST_CASES = [
    ("Hôm nay là ngày mấy?", "employee", "PHẢI gọi get_current_date"),
    ("Tìm giúp tôi thông tin về MFA trong tài liệu nội bộ", "employee", "PHẢI gọi search_policy"),
]

for question, role, expectation in TEST_CASES:
    print(f"=== Câu hỏi: {question!r} | Role: {role} ===")
    print(f"Kỳ vọng: {expectation}")
    answer = generate_answer_with_tools(SYSTEM_PROMPT, question, user_role=role)
    print(f"Trả lời: {answer}\n")