import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Projects from "./Projects";
import * as projectApi from "../../api/projectApi";
import type { Project } from "../../types/project";

const logout = vi.fn();

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ user: { username: "alice" }, logout }),
}));

vi.mock("../../api/projectApi");

const mockedProjects = vi.mocked(projectApi);

function makeProject(overrides: Partial<Project> = {}): Project {
  return {
    id: 1,
    name: "Сайт",
    description: null,
    owner_id: 1,
    task_count: 0,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

function renderPage() {
  return render(
    <MemoryRouter>
      <Projects />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("Projects page", () => {
  it("edits a project and reflects the update in the card", async () => {
    mockedProjects.getProjects.mockResolvedValue([
      makeProject({ id: 1, name: "Сайт", description: "Старое описание" }),
    ]);
    mockedProjects.updateProject.mockResolvedValue(
      makeProject({ id: 1, name: "Новый сайт", description: "Новое описание" }),
    );

    renderPage();
    const card = (await screen.findByText("Сайт")).closest("li")!;

    await userEvent.click(within(card).getByRole("button", { name: "Изменить" }));

    const nameInput = within(card).getByPlaceholderText("Название проекта");
    await userEvent.clear(nameInput);
    await userEvent.type(nameInput, "Новый сайт");

    const descInput = within(card).getByPlaceholderText("Описание (необязательно)");
    await userEvent.clear(descInput);
    await userEvent.type(descInput, "Новое описание");

    await userEvent.click(within(card).getByRole("button", { name: "Сохранить" }));

    await waitFor(() =>
      expect(mockedProjects.updateProject).toHaveBeenCalledWith(1, {
        name: "Новый сайт",
        description: "Новое описание",
      }),
    );
    expect(await screen.findByText("Новый сайт")).toBeInTheDocument();
    expect(screen.getByText("Новое описание")).toBeInTheDocument();
  });

  it("cancels editing without calling the API", async () => {
    mockedProjects.getProjects.mockResolvedValue([makeProject({ id: 1, name: "Сайт" })]);

    renderPage();
    const card = (await screen.findByText("Сайт")).closest("li")!;

    await userEvent.click(within(card).getByRole("button", { name: "Изменить" }));
    await userEvent.type(within(card).getByPlaceholderText("Название проекта"), " черновик");
    await userEvent.click(within(card).getByRole("button", { name: "Отмена" }));

    expect(mockedProjects.updateProject).not.toHaveBeenCalled();
    expect(screen.getByText("Сайт")).toBeInTheDocument();
  });
});
