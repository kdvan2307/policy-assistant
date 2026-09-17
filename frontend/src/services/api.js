export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Wrapper quanh fetch() — tự đính kèm Authorization header, và tự xử lý
 * trường hợp token hết hạn/không hợp lệ (401) bằng cách xóa token + điều
 * hướng về /login, để MỌI nơi gọi API không phải tự lặp lại logic này.
 */
export async function authFetch(path, options = {}, token) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch (networkError) {
    throw new Error("Không thể kết nối tới server. Kiểm tra backend đã chạy chưa.");
  }

  if (response.status === 401) {
    // Token hết hạn/không hợp lệ — dọn dẹp phía client, để component gọi
    // hàm này tự điều hướng (không import next/navigation ở đây vì đây là
    // module thuần, không phải React component).
    const { clearToken } = await import("./auth");
    clearToken();
    throw new Error("__UNAUTHORIZED__"); // đánh dấu đặc biệt để component nhận biết
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail || `Lỗi từ server (mã ${response.status}).`;
    throw new Error(message);
  }

  return response.json();
}

export async function login(email, password) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  } catch (networkError) {
    throw new Error("Không thể kết nối tới server. Kiểm tra backend đã chạy chưa.");
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail || `Đăng nhập thất bại (mã ${response.status}).`);
  }

  return response.json();
}

export async function sendChatMessage(message, sessionId, token) {
  return authFetch(
    "/chat",
    { method: "POST", body: JSON.stringify({ message, session_id: sessionId }) },
    token
  );
}

export async function sendFeedback(messageId, isHelpful, token) {
  return authFetch(
    "/chat/feedback",
    {
      method: "POST",
      body: JSON.stringify({ message_id: messageId, is_helpful: isHelpful }),
    },
    token
  );
}
export async function getDocuments(token) {
  return authFetch("/admin/documents", { method: "GET" }, token);
}

export async function uploadDocument(title, allowedRoles, file, token) {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("allowed_roles", allowedRoles);
  formData.append("file", file);

  // KHÔNG set "Content-Type" thủ công cho multipart — trình duyệt tự thêm
  // boundary chính xác khi thấy body là FormData; tự set sẽ làm hỏng request.
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/admin/documents`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
  } catch (networkError) {
    throw new Error("Không thể kết nối tới server.");
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail || `Upload thất bại (mã ${response.status}).`);
  }
  return response.json();
}

export async function getLogs(filters, token) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") params.append(key, value);
  });
  return authFetch(`/admin/logs?${params.toString()}`, { method: "GET" }, token);
}

export async function getUsers(token) {
  return authFetch("/admin/users", { method: "GET" }, token);
}

export async function updateUserRole(userId, role, token) {
  return authFetch(`/admin/users/${userId}/role`, { method: "PATCH", body: JSON.stringify({ role }) }, token);
}
export async function getFeedbackStats(token) {
  return authFetch("/admin/feedback-stats", { method: "GET" }, token);
}
export async function getSessions(token) {
  return authFetch("/chat/sessions", { method: "GET" }, token);
}

export async function getSessionMessages(sessionId, token) {
  return authFetch(`/chat/sessions/${sessionId}/messages`, { method: "GET" }, token);
}