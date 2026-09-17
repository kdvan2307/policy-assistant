"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/services/api";
import { saveToken } from "@/services/auth";

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);

    try {
      const result = await login(email, password);
      saveToken(result.access_token);
      router.push("/chat"); // điều hướng phía client, không tải lại trang
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm flex flex-col gap-3">
      <div className="flex flex-col gap-1">
        <label className="text-sm text-slate-400">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isLoading}
          placeholder="ban@company.com"
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 disabled:opacity-50"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm text-slate-400">Mật khẩu</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={isLoading}
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 disabled:opacity-50"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="mt-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
      >
        {isLoading ? "Đang đăng nhập..." : "Đăng nhập"}
      </button>

      {errorMessage && (
        <p className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded-lg px-3 py-2">
          {errorMessage}
        </p>
      )}
    </form>
  );
}