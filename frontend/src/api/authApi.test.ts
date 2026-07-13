import { describe, it, expect, vi, beforeEach } from "vitest";
import * as authApi from "./authApi";
import { api } from "./client";
import type { User } from "../types/user";

vi.mock("./client", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

const sampleUser: User = {
  id: 1,
  username: "alice",
  email: "alice@example.com",
  role: "user",
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("auth api", () => {
  it("register posts payload and returns user", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: sampleUser });

    const result = await authApi.register({
      username: "alice",
      email: "alice@example.com",
      password: "password123",
    });

    expect(mockedApi.post).toHaveBeenCalledWith("/auth/register", {
      username: "alice",
      email: "alice@example.com",
      password: "password123",
    });
    expect(result).toEqual(sampleUser);
  });

  it("login posts credentials and returns token", async () => {
    const token = { access_token: "abc", token_type: "bearer" };
    mockedApi.post.mockResolvedValueOnce({ data: token });

    const result = await authApi.login({
      email: "alice@example.com",
      password: "password123",
    });

    expect(mockedApi.post).toHaveBeenCalledWith("/auth/login", {
      email: "alice@example.com",
      password: "password123",
    });
    expect(result).toEqual(token);
  });

  it("getMe fetches the current user", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: sampleUser });

    const result = await authApi.getMe();

    expect(mockedApi.get).toHaveBeenCalledWith("/auth/me");
    expect(result).toEqual(sampleUser);
  });
});
