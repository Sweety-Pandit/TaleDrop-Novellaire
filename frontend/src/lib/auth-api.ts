import { api } from "@/lib/api";
import type { Tokens, User, UserRole } from "@/types";

export interface RegisterPayload {
  username: string;
  display_name: string;
  email: string;
  password: string;
  role?: Extract<UserRole, "READER" | "AUTHOR">;
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const { data } = await api.post<User>("/auth/register", payload);
  return data;
}

export async function loginUser(email: string, password: string): Promise<Tokens> {
  // The backend's /auth/login uses the OAuth2 password flow, which expects
  // form-encoded data with the email sent as `username` — not JSON.
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const { data } = await api.post<Tokens>("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/users/me");
  return data;
}

export async function logoutUser(): Promise<void> {
  await api.post("/auth/logout");
}
