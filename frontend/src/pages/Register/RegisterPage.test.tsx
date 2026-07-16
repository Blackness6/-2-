import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import RegisterPage from "./RegisterPage";

const navigate = vi.fn();
const register = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => navigate };
});

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ register }),
}));

function renderRegister() {
  return render(
    <MemoryRouter>
      <RegisterPage />
    </MemoryRouter>,
  );
}

async function fillForm() {
  await userEvent.type(screen.getByLabelText("Имя пользователя"), "carol");
  await userEvent.type(screen.getByLabelText("Email"), "carol@example.com");
  await userEvent.type(screen.getByLabelText("Пароль"), "password123");
  await userEvent.click(screen.getByRole("button", { name: "Зарегистрироваться" }));
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("Register page", () => {
  it("submits the form and navigates home on success", async () => {
    register.mockResolvedValueOnce(undefined);
    renderRegister();

    await fillForm();

    await waitFor(() =>
      expect(register).toHaveBeenCalledWith("carol", "carol@example.com", "password123"),
    );
    expect(navigate).toHaveBeenCalledWith("/");
  });

  it("shows the server error message on failure", async () => {
    register.mockRejectedValueOnce({ response: { data: { detail: "Email уже занят" } } });
    renderRegister();

    await fillForm();

    expect(await screen.findByText("Email уже занят")).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("shows a fallback error when the server gives no detail", async () => {
    register.mockRejectedValueOnce(new Error("network"));
    renderRegister();

    await fillForm();

    expect(await screen.findByText("Не удалось зарегистрироваться")).toBeInTheDocument();
  });
});