import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthProvider, useAuth } from "./AuthContext";
import * as authApi from "../api/auth";
import type { User } from "../api/types";

vi.mock("../api/auth");

const mockedAuth = vi.mocked(authApi);

const sampleUser: User = {
  id: 1,
  username: "alice",
  email: "alice@example.com",
  role: "user",
};

function Consumer() {
  const { user, loading, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="loading">{loading ? "loading" : "ready"}</span>
      <span data-testid="user">{user ? user.username : "anonymous"}</span>
      <button onClick={() => login("alice@example.com", "password123")}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <AuthProvider>
      <Consumer />
    </AuthProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("AuthContext", () => {
  it("stays anonymous when no token is stored", async () => {
    renderWithProvider();

    await waitFor(() => expect(screen.getByTestId("loading")).toHaveTextContent("ready"));
    expect(screen.getByTestId("user")).toHaveTextContent("anonymous");
    expect(mockedAuth.getMe).not.toHaveBeenCalled();
  });

  it("loads the user from a stored token", async () => {
    localStorage.setItem("token", "existing-token");
    mockedAuth.getMe.mockResolvedValueOnce(sampleUser);

    renderWithProvider();

    await waitFor(() => expect(screen.getByTestId("user")).toHaveTextContent("alice"));
    expect(screen.getByTestId("loading")).toHaveTextContent("ready");
  });

  it("clears an invalid token", async () => {
    localStorage.setItem("token", "bad-token");
    mockedAuth.getMe.mockRejectedValueOnce(new Error("401"));

    renderWithProvider();

    await waitFor(() => expect(screen.getByTestId("loading")).toHaveTextContent("ready"));
    expect(screen.getByTestId("user")).toHaveTextContent("anonymous");
    expect(localStorage.getItem("token")).toBeNull();
  });

  it("login stores the token and sets the user", async () => {
    mockedAuth.login.mockResolvedValueOnce({ access_token: "new-token", token_type: "bearer" });
    mockedAuth.getMe.mockResolvedValueOnce(sampleUser);

    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId("loading")).toHaveTextContent("ready"));

    await userEvent.click(screen.getByText("login"));

    await waitFor(() => expect(screen.getByTestId("user")).toHaveTextContent("alice"));
    expect(localStorage.getItem("token")).toBe("new-token");
  });

  it("logout clears the token and user", async () => {
    localStorage.setItem("token", "existing-token");
    mockedAuth.getMe.mockResolvedValueOnce(sampleUser);

    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId("user")).toHaveTextContent("alice"));

    await userEvent.click(screen.getByText("logout"));

    expect(screen.getByTestId("user")).toHaveTextContent("anonymous");
    expect(localStorage.getItem("token")).toBeNull();
  });
});
