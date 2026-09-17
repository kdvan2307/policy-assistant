"use client";

import { useState } from "react";
import AdminGuard from "@/components/AdminGuard";
import UploadTab from "@/components/admin/UploadTab";
import LogsTab from "@/components/admin/LogsTab";
import UsersTab from "@/components/admin/UsersTab";
import FeedbackStatsTab from "@/components/admin/FeedbackStatsTab";

const TABS = [
  { key: "upload", label: "Upload tài liệu" },
  { key: "logs", label: "Xem log" },
  { key: "users", label: "Quản lý User" },
  { key: "feedback", label: "Thống kê phản hồi" },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("upload");

  return (
    <AdminGuard>
      {(token) => (
        <main className="min-h-screen px-6 py-8 max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-emerald-400 mb-6">Trang Quản trị</h1>

          <div className="flex gap-2 border-b border-slate-800 mb-6">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? "border-emerald-500 text-emerald-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === "upload" && <UploadTab token={token} />}
          {activeTab === "logs" && <LogsTab token={token} />}
          {activeTab === "users" && <UsersTab token={token} />}
          {activeTab === "feedback" && <FeedbackStatsTab token={token} />}
        </main>
      )}
    </AdminGuard>
  );
}