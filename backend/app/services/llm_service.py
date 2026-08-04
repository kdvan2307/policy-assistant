import json
import os

import ollama

from app.services.tools.tool_specs import TOOL_SPECS
from app.services.tool_manager import execute_tool

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "qwen2.5:3b-instruct"

_client = ollama.Client(host=OLLAMA_HOST)


def generate_answer(system_prompt: str, user_message: str) -> str:
    """Giữ nguyên từ Bước 9 — gọi thẳng, không có tool."""
    response = _client.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response["message"]["content"]


def generate_answer_with_tools(system_prompt: str, user_message: str, user_role: str) -> str:
    """Cho phép model tự quyết định gọi tool nào (nếu cần) trước khi trả lời.

    Luồng: gửi câu hỏi kèm TOOL_SPECS -> model TỰ QUYẾT ĐỊNH có cần gọi tool
    không -> nếu có, thực thi tool thật -> đưa kết quả tool trở lại cho model
    -> model tổng hợp câu trả lời cuối cùng dựa trên kết quả đó.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    first_response = _client.chat(model=MODEL_NAME, messages=messages, tools=TOOL_SPECS)
    message = first_response["message"]

    tool_calls = message.get("tool_calls")
    if not tool_calls:
        # Model không thấy cần tool nào -> trả lời thẳng, giống generate_answer thường
        return message["content"]

    messages.append(message)

    for call in tool_calls:
        tool_name = call["function"]["name"]
        tool_args = call["function"]["arguments"]

        result = execute_tool(tool_name, tool_args, user_role)

        messages.append({
            "role": "tool",
            "content": json.dumps(result, ensure_ascii=False),
        })

    final_response = _client.chat(model=MODEL_NAME, messages=messages)
    return final_response["message"]["content"]