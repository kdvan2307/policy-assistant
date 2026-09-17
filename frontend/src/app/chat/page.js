"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, clearToken } from "@/services/auth";
import ChatWindow from "@/components/ChatWindow";
import ChatHistorySidebar from "@/components/ChatHistorySidebar";

export default function ChatPage() {
  const router = useRouter();
  const [token, setToken] = useState(null);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  useEffect(() => {
    const savedToken = getToken();

    if (!savedToken) {
      router.push("/login");
      return;
    }

    setToken(savedToken);

    // Khôi phục cuộc trò chuyện đang mở trước khi F5
    const savedSessionId = localStorage.getItem("activeSessionId");

    if (savedSessionId) {
      setActiveSessionId(Number(savedSessionId));
    }
  }, [router]);

  if (!token) return null;

  // Người dùng chọn một cuộc trò chuyện trong sidebar
  const handleSelectSession = (sessionId) => {
    setActiveSessionId(sessionId);

    // Ghi nhớ cuộc trò chuyện đang mở
    localStorage.setItem("activeSessionId", String(sessionId));
  };

  // Người dùng bấm "+ Cuộc trò chuyện mới"
  const handleNewChat = () => {
    setActiveSessionId(null);

    // Xóa session đang nhớ
    localStorage.removeItem("activeSessionId");
  };

  // Backend vừa tạo session mới sau câu hỏi đầu tiên
  const handleSessionCreated = (newSessionId) => {
    setActiveSessionId(newSessionId);

    // Ghi nhớ session mới
    localStorage.setItem("activeSessionId", String(newSessionId));

    // Ép sidebar tải lại danh sách
    setSidebarRefreshKey((k) => k + 1);
  };

  const handleLogout = () => {
    clearToken();
    localStorage.removeItem("activeSessionId");
    router.push("/login");
  };

  return (
    <div className="flex h-screen">
      <ChatHistorySidebar
        token={token}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        refreshKey={sidebarRefreshKey}
      />

      <div className="flex flex-col flex-1">
        <header className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <h1 className="text-lg font-semibold text-emerald-400">
            Trợ lý Chính sách ATTT Nội bộ
          </h1>

          <button
            onClick={handleLogout}
            className="text-sm px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            Đăng xuất
          </button>
        </header>

        <ChatWindow
          token={token}
          sessionId={activeSessionId}
          onSessionCreated={handleSessionCreated}
        />
      </div>
    </div>
  );
}