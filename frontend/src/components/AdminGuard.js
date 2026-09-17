"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/services/auth";
import { authFetch } from "@/services/api";

/**
 * Chặn truy cập trang Admin ở phía frontend NGAY khi phát hiện role không
 * phải admin — lớp bảo vệ này chỉ để tránh hiện giao diện quản trị "lộ ra"
 * trước khi API từ chối; backend (require_role) vẫn là lớp bảo vệ THẬT SỰ
 * đáng tin cậy, không thể bị bỏ qua dù ai đó sửa code frontend.
 */
export default function AdminGuard({ children }) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [isAllowed, setIsAllowed] = useState(false);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const check = async () => {
      const savedToken = getToken();
      if (!savedToken) {
        router.push("/login");
        return;
      }

      try {
        // Dùng chính /admin/ping (Bước 4) làm phép thử — nếu role không phải
        // Admin, API này tự trả 403, không cần route riêng để "kiểm tra role".
        await authFetch("/admin/ping", { method: "GET" }, savedToken);
        setToken(savedToken);
        setIsAllowed(true);
      } catch (error) {
        router.push("/chat"); // không đủ quyền -> đá về trang chat thường
      } finally {
        setIsChecking(false);
      }
    };
    check();
  }, [router]);

  if (isChecking) return null;
  if (!isAllowed) return null;

  return children(token);
}