"use client";

import { useState } from "react";
import { sendFeedback } from "@/services/api";

export default function FeedbackButtons({ messageId, token }) {
  // null = chưa đánh giá, true = đã bấm up, false = đã bấm down
  const [feedback, setFeedback] = useState(null);
  const [isSending, setIsSending] = useState(false);

  const handleClick = async (isHelpful) => {
    if (isSending) return;

    const previousFeedback = feedback;
    setFeedback(isHelpful); // optimistic update — đổi trạng thái nút NGAY
    setIsSending(true);

    try {
      await sendFeedback(messageId, isHelpful, token);
    } catch (error) {
      setFeedback(previousFeedback); // rollback nếu API lỗi
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="mt-2 pt-2 border-t border-slate-700 flex items-center gap-2">
      <span className="text-xs text-slate-500">Câu trả lời này có hữu ích không?</span>
      <button
        onClick={() => handleClick(true)}
        disabled={isSending}
        aria-label="Hữu ích"
        className={`text-sm px-2 py-1 rounded-lg transition-colors ${
          feedback === true
            ? "bg-emerald-600 text-white"
            : "bg-slate-700 text-slate-400 hover:bg-slate-600"
        }`}
      >
        👍
      </button>
      <button
        onClick={() => handleClick(false)}
        disabled={isSending}
        aria-label="Không hữu ích"
        className={`text-sm px-2 py-1 rounded-lg transition-colors ${
          feedback === false
            ? "bg-red-600 text-white"
            : "bg-slate-700 text-slate-400 hover:bg-slate-600"
        }`}
      >
        👎
      </button>
    </div>
  );
}