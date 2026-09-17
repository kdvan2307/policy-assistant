import ReactMarkdown from "react-markdown";
import FeedbackButtons from "./FeedbackButtons";

export default function ChatMessageBubble({ role, content, sources, messageId, token }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-emerald-600 text-white rounded-br-sm"
            : "bg-slate-800 text-slate-100 rounded-bl-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-ul:my-1">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}

        {!isUser && sources?.length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-700 flex flex-wrap gap-1.5">
            {sources.map((source, i) => (
              <span key={i} className="text-xs px-2 py-0.5 bg-slate-700 text-slate-300 rounded-full">
                📄 {source}
              </span>
            ))}
          </div>
        )}

        {/* Chỉ tin nhắn assistant CÓ messageId mới hiện nút feedback — tin
            nhắn user không cần, và messageId chỉ có sau khi API trả lời xong
            (không có ở tin nhắn user optimistic update). */}
        {!isUser && messageId && <FeedbackButtons messageId={messageId} token={token} />}
      </div>
    </div>
  );
}