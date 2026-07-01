import { api } from "./api";
import type { User } from "./types";

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function register(payload: RegisterPayload) {
  const { data } = await api.post<User>("/auth/register", payload);
  return data;
}

export async function login(payload: LoginPayload) {
  const { data } = await api.post<{ access_token: string; token_type: string }>(
    "/auth/login",
    payload,
  );
  return data;
}

export async function getMe() {
  const { data } = await api.get<User>("/auth/me");
  return data;
}
