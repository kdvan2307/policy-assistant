const TOKEN_KEY = "policy_assistant_token";

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  if (typeof window === "undefined") return null; // an toàn khi chạy ở server (SSR)
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}