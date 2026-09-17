export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-4 px-4">
      <h1 className="text-3xl font-bold text-emerald-400">
        Trợ lý AI Chính sách ATTT Nội bộ
      </h1>
      <p className="text-slate-300">
        Frontend đã khởi tạo thành công với Next.js + TailwindCSS.
      </p>
      <button className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 rounded-lg font-medium transition-colors">
        Nút test Tailwind
      </button>
    </main>
  );
}