import type { ChatHistoryMessage, ChatReply, Product, User } from "./types";

export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // fall through to generic message
  }
  return "Something went wrong";
}

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE_URL}/api/products`);
  if (!res.ok) throw new Error("Failed to load products");
  return res.json();
}

export async function fetchProduct(productId: string): Promise<Product> {
  const res = await fetch(`${API_BASE_URL}/api/products/${productId}`);
  if (!res.ok) throw new Error("Failed to load product");
  return res.json();
}

export function productImageUrl(imageUrl: string): string {
  return `${API_BASE_URL}${imageUrl}`;
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new ApiError(await parseErrorDetail(res));
  return res.json();
}

export async function loginUser(payload: LoginPayload): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new ApiError(await parseErrorDetail(res));
  return res.json();
}

export async function sendChatMessage(
  message: string,
  userId: number | null,
  currentProductId: string | null,
): Promise<ChatReply> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, user_id: userId, current_product_id: currentProductId }),
  });
  if (!res.ok) throw new ApiError(await parseErrorDetail(res));
  return res.json();
}

export async function fetchChatHistory(userId: number): Promise<ChatHistoryMessage[]> {
  const res = await fetch(`${API_BASE_URL}/api/chat/history?user_id=${userId}`);
  if (!res.ok) throw new ApiError(await parseErrorDetail(res));
  return res.json();
}
