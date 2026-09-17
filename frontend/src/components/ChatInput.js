"use client";

import { useState } from "react";

export default function ChatInput({ onSend, isLoading }) {
  const [value, setValue] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;

    onSend(trimmed);
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t border-slate-800">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={isLoading}
        placeholder="Hỏi về chính sách, quy trình an toàn thông tin..."
        className="flex-1 px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={isLoading || !value.trim()}
        className="px-5 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
      >
        {isLoading ? "..." : "Gửi"}
      </button>
    </form>
  );
}