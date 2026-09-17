"use client";

import { useEffect, useState } from "react";
import { getSessions } from "@/services/api";

export default function ChatHistorySidebar({ token, activeSessionId, onSelectSession, onNewChat, refreshKey }) {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    getSessions(token)
      .then(setSessions)
      .catch(() => setSessions([]));
    // refreshKey thay đổi mỗi khi có session MỚI được tạo (lượt hỏi đầu tiên
    // của 1 cuộc trò chuyện) — trigger tải lại danh sách để session mới hiện ra.
  }, [token, refreshKey]);

  return (
    <aside className="w-64 border-r border-slate-800 flex flex-col h-screen bg-slate-950/50">
      <div className="p-3 border-b border-slate-800">
        <button
          onClick={onNewChat}
          className="w-full px-3 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium text-white transition-colors"
        >
          + Cuộc trò chuyện mới
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
        {sessions.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelectSession(s.id)}
            className={`text-left px-3 py-2 rounded-lg text-sm truncate transition-colors ${
              s.id === activeSessionId
                ? "bg-slate-800 text-white"
                : "text-slate-400 hover:bg-slate-800/50"
            }`}
          >
            {s.title || `Cuộc trò chuyện #${s.id}`}
          </button>
        ))}
        {sessions.length === 0 && (
          <p className="text-slate-600 text-xs px-3 py-2">Chưa có cuộc trò chuyện nào.</p>
        )}
      </div>
    </aside>
  );
}