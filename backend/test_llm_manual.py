from app.services.llm_service import generate_answer

response = generate_answer(
    system_prompt="Bạn là trợ lý AI tra cứu chính sách an toàn thông tin nội bộ. Trả lời ngắn gọn.",
    user_message="Mật khẩu cần tối thiểu bao nhiêu ký tự theo chính sách công ty?",
)

print("=== Phản hồi từ model ===")
print(response)