"use client";

import { useState } from "react";
import { getLogs } from "@/services/api";

export default function LogsTab({ token }) {
  const [endpoint, setEndpoint] = useState("");
  const [hasError, setHasError] = useState("");
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const filters = { endpoint, limit: 50 };
      if (hasError !== "") filters.has_error = hasError;
      const results = await getLogs(filters, token);
      setLogs(results);
    } catch (error) {
      setLogs([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2 flex-wrap">
        <input
          type="text"
          placeholder="Lọc theo endpoint (vd: chat)"
          value={endpoint}
          onChange={(e) => setEndpoint(e.target.value)}
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
        />
        <select
          value={hasError}
          onChange={(e) => setHasError(e.target.value)}
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm"
        >
          <option value="">Tất cả</option>
          <option value="true">Chỉ lỗi</option>
          <option value="false">Chỉ thành công</option>
        </select>
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 rounded-lg text-sm font-medium"
        >
          {isLoading ? "Đang tải..." : "Lọc"}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-slate-400 border-b border-slate-700">
            <tr>
              <th className="py-2 pr-4">Method</th>
              <th className="py-2 pr-4">Endpoint</th>
              <th className="py-2 pr-4">Status</th>
              <th className="py-2 pr-4">Thời gian (ms)</th>
              <th className="py-2 pr-4">Lúc</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-slate-800">
                <td className="py-2 pr-4">{log.method}</td>
                <td className="py-2 pr-4">{log.endpoint}</td>
                <td className={`py-2 pr-4 ${log.status_code >= 400 ? "text-red-400" : "text-emerald-400"}`}>
                  {log.status_code}
                </td>
                <td className="py-2 pr-4">{log.duration_ms}</td>
                <td className="py-2 pr-4 text-slate-400">{new Date(log.created_at).toLocaleString("vi-VN")}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan={5} className="py-4 text-center text-slate-500">Chưa có dữ liệu — bấm &quot;Lọc&quot; để tải log.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}