from datetime import datetime

_WEEKDAY_VI = {
    "Monday": "Thứ Hai", "Tuesday": "Thứ Ba", "Wednesday": "Thứ Tư",
    "Thursday": "Thứ Năm", "Friday": "Thứ Sáu", "Saturday": "Thứ Bảy", "Sunday": "Chủ Nhật",
}


def get_current_date() -> dict:
    """Trả về ngày hiện tại — LLM không tự biết thông tin này vì kiến thức
    của model 'đóng băng' tại thời điểm huấn luyện."""
    now = datetime.now()
    return {
        "date": now.strftime("%d/%m/%Y"),
        "weekday": _WEEKDAY_VI.get(now.strftime("%A"), now.strftime("%A")),
    }