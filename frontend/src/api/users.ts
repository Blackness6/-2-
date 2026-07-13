import { api } from "./api";
import type { UserShort } from "./types";

export async function getUsers() {
  const { data } = await api.get<UserShort[]>("/api/users");
  return data;
}
