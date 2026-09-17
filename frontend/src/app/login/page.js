import LoginForm from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 px-4">
      <h1 className="text-2xl font-bold text-emerald-400">
        Đăng nhập — Trợ lý AI Chính sách ATTT
      </h1>
      <LoginForm />
    </main>
  );
}