# Quy trình Ứng phó Sự cố An toàn Thông tin

**Mã tài liệu:** PROC-IR-002
**Phiên bản:** 2.0
**Áp dụng cho:** Đội ngũ An toàn Thông tin, Quản lý hệ thống

> Tài liệu này ở mức bảo mật nội bộ hạn chế — chỉ dành cho Security Manager
> và Admin, do chứa quy trình xử lý sự cố có thể bị lợi dụng nếu lộ ra ngoài.

## 1. Phân loại mức độ nghiêm trọng

| Mức | Mô tả | Thời gian phản hồi |
|---|---|---|
| P1 - Nghiêm trọng | Rò rỉ dữ liệu, hệ thống ngừng hoạt động toàn bộ | 15 phút |
| P2 - Cao | Truy cập trái phép được phát hiện, mã độc lan rộng | 1 giờ |
| P3 - Trung bình | Bất thường về lưu lượng, cảnh báo từ hệ thống giám sát | 4 giờ |
| P4 - Thấp | Vi phạm chính sách nhỏ, không ảnh hưởng vận hành | 1 ngày làm việc |

## 2. Các bước xử lý

### Bước 1 — Phát hiện và ghi nhận
Ghi lại thời điểm phát hiện, nguồn phát hiện (SIEM, người dùng báo cáo, đối tác
thứ ba), tạo mã sự cố theo định dạng `INC-YYYYMMDD-NNN`.

### Bước 2 — Phân loại và đánh giá phạm vi
Xác định mức độ nghiêm trọng (P1-P4), hệ thống/dữ liệu bị ảnh hưởng, số lượng
người dùng liên quan.

### Bước 3 — Ngăn chặn (Containment)
- Cô lập hệ thống bị ảnh hưởng khỏi mạng nội bộ nếu cần
- Vô hiệu hóa tài khoản nghi ngờ bị chiếm quyền
- Chặn IP/domain độc hại tại firewall

### Bước 4 — Khắc phục (Eradication & Recovery)
Loại bỏ nguyên nhân gốc (mã độc, lỗ hổng), khôi phục hệ thống từ bản sao lưu
sạch, xác nhận hệ thống hoạt động bình thường trước khi đưa trở lại sản xuất.

### Bước 5 — Báo cáo sau sự cố
Trong vòng 48 giờ sau khi xử lý xong, lập báo cáo gồm: nguyên nhân gốc,
timeline xử lý, thiệt hại ước tính, bài học kinh nghiệm và hành động khắc phục
phòng ngừa tái diễn.

## 3. Kênh liên lạc khẩn cấp

- Hotline An toàn Thông tin (24/7): nội bộ máy lẻ 1900
- Kênh Slack: #security-incident
- Email escalation: ciso@company.internal
