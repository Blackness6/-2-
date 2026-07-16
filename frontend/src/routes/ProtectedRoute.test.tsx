import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";

const useAuthMock = vi.fn();

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => useAuthMock(),
}));

function renderProtected() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <div>Секретная страница</div>
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<div>Страница входа</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProtectedRoute", () => {
  it("shows a loader while auth state is loading", () => {
    useAuthMock.mockReturnValue({ user: null, loading: true });
    renderProtected();

    expect(screen.getByText("Загрузка...")).toBeInTheDocument();
    expect(screen.queryByText("Секретная страница")).not.toBeInTheDocument();
  });

  it("redirects to /login when there is no user", () => {
    useAuthMock.mockReturnValue({ user: null, loading: false });
    renderProtected();

    expect(screen.getByText("Страница входа")).toBeInTheDocument();
    expect(screen.queryByText("Секретная страница")).not.toBeInTheDocument();
  });

  it("renders the protected content for an authenticated user", () => {
    useAuthMock.mockReturnValue({
      user: { id: 1, username: "alice", email: "alice@example.com", role: "user" },
      loading: false,
    });
    renderProtected();

    expect(screen.getByText("Секретная страница")).toBeInTheDocument();
  });
});