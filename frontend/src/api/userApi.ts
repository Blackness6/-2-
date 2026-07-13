import { api } from "./client";
import type { UserShort } from "../types/user";

export async function getUsers() {
  const { data } = await api.get<UserShort[]>("/api/users");
  return data;
}
