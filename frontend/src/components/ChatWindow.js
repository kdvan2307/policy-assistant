"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { sendChatMessage, getSessionMessages } from "@/services/api";
import ChatMessageBubble from "./ChatMessageBubble";
import ChatInput from "./ChatInput";

export default function ChatWindow({ token, sessionId, onSessionCreated }) {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const scrollRef = useRef(null);

  // Mỗi khi sessionId đổi (chọn session khác từ sidebar, hoặc bấm "cuộc trò
  // chuyện mới" -> sessionId = null) -> tải lại đúng lịch sử tương ứng.
  useEffect(() => {
    if (sessionId === null) {
      setMessages([]); // cuộc trò chuyện mới -> màn hình trống
      return;
    }

    getSessionMessages(sessionId, token)
      .then((history) => {
        setMessages(
          history.map((m) => ({
            role: m.role,
            content: m.content,
            sources: m.sources,
            messageId: m.id,
          }))
        );
      })
      .catch((error) => {
        if (error.message === "__UNAUTHORIZED__") router.push("/login");
      });
  }, [sessionId, token, router]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (question) => {
    setErrorMessage(null);

    const userMessage = { role: "user", content: question, sources: [], messageId: null };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await sendChatMessage(question, sessionId, token);

      // Nếu đây là lượt hỏi ĐẦU TIÊN của 1 cuộc trò chuyện mới (sessionId
      // trước đó là null), báo lên component cha để cập nhật sessionId hiện
      // tại + refresh sidebar — không tự quản lý sessionId ở đây nữa.
      if (sessionId === null) {
        onSessionCreated(result.session_id);
      }

      const assistantMessage = {
        role: "assistant",
        content: result.answer,
        sources: result.sources,
        messageId: result.message_id,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      if (error.message === "__UNAUTHORIZED__") {
        router.push("/login");
        return;
      }
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen flex-1">
      <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-4">
        {messages.length === 0 && (
          <p className="text-slate-500 text-center mt-10">
            Đặt câu hỏi về chính sách hoặc quy trình an toàn thông tin nội bộ.
          </p>
        )}

        {messages.map((msg, i) => (
          <ChatMessageBubble
            key={msg.messageId ?? `local-${i}`}
            role={msg.role}
            content={msg.content}
            sources={msg.sources}
            messageId={msg.messageId}
            token={token}
          />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" />
            </div>
          </div>
        )}

        {errorMessage && (
          <p className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded-lg px-3 py-2 self-center">
            {errorMessage}
          </p>
        )}

        <div ref={scrollRef} />
      </div>

      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
}