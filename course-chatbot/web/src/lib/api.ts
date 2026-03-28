import type { ChatRequest, ChatResponse } from "../types/chat";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

type ApiErrorResponse = {
  detail?: string;
};

export async function chatWithCourseBot(
  payload: ChatRequest
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  let data: ChatResponse | ApiErrorResponse | null = null;

  try {
    data = await response.json();
    console.log("API /chat response:", data);
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      (data as ApiErrorResponse | null)?.detail || "ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้"
    );
  }

  return data as ChatResponse;
}