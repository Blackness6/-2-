import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "./LoginPage";

const navigate = vi.fn();
const login = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => navigate };
});

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ login }),
}));

function renderLogin() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("Login page", () => {
  it("submits credentials and navigates home on success", async () => {
    login.mockResolvedValueOnce(undefined);
    renderLogin();

    await userEvent.type(screen.getByLabelText("Email"), "alice@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Войти" }));

    await waitFor(() =>
      expect(login).toHaveBeenCalledWith("alice@example.com", "password123"),
    );
    expect(navigate).toHaveBeenCalledWith("/");
  });

  it("shows the server error message on failure", async () => {
    login.mockRejectedValueOnce({ response: { data: { detail: "Неверный пароль" } } });
    renderLogin();

    await userEvent.type(screen.getByLabelText("Email"), "alice@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: "Войти" }));

    expect(await screen.findByText("Неверный пароль")).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("shows a fallback error when the server gives no detail", async () => {
    login.mockRejectedValueOnce(new Error("network"));
    renderLogin();

    await userEvent.type(screen.getByLabelText("Email"), "alice@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Войти" }));

    expect(await screen.findByText("Не удалось войти")).toBeInTheDocument();
  });
});
