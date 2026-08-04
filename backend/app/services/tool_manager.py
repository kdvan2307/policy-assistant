from typing import Callable

from app.services.tools.date_tool import get_current_date
from app.services.tools.policy_search_tool import search_policy

# Registry pattern — giống hệt tinh thần đã áp dụng ở project Recon (Bước 15):
# tra cứu bằng dict, KHÔNG dùng if/elif. Thêm tool mới = thêm 1 dòng vào đây.
_EXECUTORS: dict[str, Callable[[dict, str], dict]] = {
    "get_current_date": lambda args, user_role: get_current_date(),
    "search_policy": lambda args, user_role: search_policy(
        keyword=args.get("keyword", ""), user_role=user_role
    ),
}


def execute_tool(tool_name: str, arguments: dict, user_role: str) -> dict:
    """Điểm gọi duy nhất — user_role LUÔN được tiêm từ backend (session đã
    xác thực ở Bước 3), KHÔNG bao giờ lấy từ `arguments` (dữ liệu do LLM sinh
    ra, không đáng tin cho mục đích phân quyền)."""
    executor = _EXECUTORS.get(tool_name)
    if executor is None:
        return {"error": f"Tool '{tool_name}' không tồn tại."}

    try:
        return executor(arguments, user_role)
    except Exception as exc:
        return {"error": f"Lỗi khi chạy tool '{tool_name}': {exc}"}