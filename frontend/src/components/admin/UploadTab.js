"use client";

import { useState } from "react";
import { uploadDocument } from "@/services/api";

const ROLE_OPTIONS = ["admin", "security_manager", "employee", "guest"];

export default function UploadTab({ token }) {
  const [title, setTitle] = useState("");
  const [selectedRoles, setSelectedRoles] = useState(["employee"]);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const toggleRole = (role) => {
    setSelectedRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(null);

    if (!file || !title.trim() || selectedRoles.length === 0) {
      setMessage({ type: "error", text: "Vui lòng nhập tiêu đề, chọn ít nhất 1 role, và chọn file." });
      return;
    }

    setIsUploading(true);
    try {
      const result = await uploadDocument(title, selectedRoles.join(","), file, token);
      setMessage({ type: "success", text: `Đã upload "${result.title}" — tạo ${result.chunks_created} chunk.` });
      setTitle("");
      setFile(null);
      setSelectedRoles(["employee"]);
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-lg">
      <div>
        <label className="text-sm text-slate-400 block mb-1">Tiêu đề tài liệu</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
        />
      </div>

      <div>
        <label className="text-sm text-slate-400 block mb-1">Quyền xem (chọn ít nhất 1)</label>
        <div className="flex flex-wrap gap-2">
          {ROLE_OPTIONS.map((role) => (
            <button
              type="button"
              key={role}
              onClick={() => toggleRole(role)}
              className={`text-sm px-3 py-1.5 rounded-lg transition-colors ${
                selectedRoles.includes(role)
                  ? "bg-emerald-600 text-white"
                  : "bg-slate-800 text-slate-400 border border-slate-700"
              }`}
            >
              {role}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-sm text-slate-400 block mb-1">Tệp (md/pdf/docx/html)</label>
        <input
          type="file"
          accept=".md,.pdf,.docx,.html"
          onChange={(e) => setFile(e.target.files[0] || null)}
          className="w-full text-sm text-slate-400"
        />
      </div>

      <button
        type="submit"
        disabled={isUploading}
        className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-600 rounded-lg font-medium transition-colors"
      >
        {isUploading ? "Đang xử lý..." : "Upload & Ingest"}
      </button>

      {message && (
        <p className={`text-sm px-3 py-2 rounded-lg ${message.type === "error" ? "bg-red-950/40 text-red-400 border border-red-900" : "bg-emerald-950/40 text-emerald-400 border border-emerald-900"}`}>
          {message.text}
        </p>
      )}
    </form>
  );
}