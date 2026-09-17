"use client";

import { useEffect, useState } from "react";
import { getFeedbackStats } from "@/services/api";

export default function FeedbackStatsTab({ token }) {
  const [stats, setStats] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    getFeedbackStats(token)
      .then(setStats)
      .catch((error) => setErrorMessage(error.message));
  }, [token]);

  if (errorMessage) {
    return <p className="text-red-400 text-sm">{errorMessage}</p>;
  }
  if (!stats) return <p className="text-slate-500 text-sm">Đang tải...</p>;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div className="bg-slate-800 rounded-lg p-4">
        <p className="text-slate-400 text-xs">Tổng đánh giá</p>
        <p className="text-2xl font-bold text-white">{stats.total}</p>
      </div>
      <div className="bg-slate-800 rounded-lg p-4">
        <p className="text-slate-400 text-xs">Hữu ích 👍</p>
        <p className="text-2xl font-bold text-emerald-400">{stats.helpful_count}</p>
      </div>
      <div className="bg-slate-800 rounded-lg p-4">
        <p className="text-slate-400 text-xs">Không hữu ích 👎</p>
        <p className="text-2xl font-bold text-red-400">{stats.not_helpful_count}</p>
      </div>
      <div className="bg-slate-800 rounded-lg p-4">
        <p className="text-slate-400 text-xs">Tỷ lệ hài lòng</p>
        <p className="text-2xl font-bold text-white">{stats.helpful_rate}%</p>
      </div>
    </div>
  );
}