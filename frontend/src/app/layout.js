import "./globals.css";

export const metadata = {
  title: "Trợ lý AI Chính sách ATTT Nội bộ",
  description: "Tra cứu Chính sách & Quy trình An toàn Thông tin Nội bộ",
};

export default function RootLayout({ children }) {
  return (
    <html lang="vi">
      <body className="bg-slate-900 text-white min-h-screen">{children}</body>
    </html>
  );
}