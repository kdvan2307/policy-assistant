from app.services.retriever_service import retrieve
from app.services.prompt_builder import build_system_prompt
from app.services.llm_service import generate_answer

TEST_CASES = [
    # (câu hỏi, role, mô tả kỳ vọng)
    ("Mật khẩu cần tối thiểu bao nhiêu ký tự?", "employee", "PHẢI trả lời đúng '12 ký tự', trích nguồn Chính sách Mật khẩu"),
    ("Quy trình xử lý sự cố có mấy bước?", "guest", "PHẢI từ chối — guest không có quyền xem tài liệu này"),
    ("Quy trình xử lý sự cố có mấy bước?", "security_manager", "PHẢI trả lời đúng '5 bước', trích nguồn Quy trình Ứng phó Sự cố"),
    ("Hôm nay nên ăn gì để giảm cân?", "admin", "PHẢI từ chối — ngoài phạm vi hỗ trợ, dù admin xem được mọi tài liệu"),
]

for question, role, expectation in TEST_CASES:
    print(f"=== Câu hỏi: {question!r} | Role: {role} ===")
    print(f"Kỳ vọng: {expectation}")

    chunks = retrieve(question, user_role=role, top_k=3)
    system_prompt = build_system_prompt(chunks)
    answer = generate_answer(system_prompt, question)

    print(f"Trả lời: {answer}\n")