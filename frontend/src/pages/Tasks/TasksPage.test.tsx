import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TasksPage from "./TasksPage";
import * as taskApi from "../../api/taskApi";
import * as userApi from "../../api/userApi";
import type { Task, TaskStats } from "../../types/task";

const logout = vi.fn();

vi.mock("../../hooks/useAuth", () => ({
  useAuth: () => ({ user: { username: "alice" }, logout }),
}));

vi.mock("../../api/taskApi");
vi.mock("../../api/userApi");

const mockedTasks = vi.mocked(taskApi);
const mockedUsers = vi.mocked(userApi);

const emptyStats: TaskStats = { TODO: 0, IN_PROGRESS: 0, DONE: 0, CANCELLED: 0 };

function makeTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 1,
    title: "Купить молоко",
    description: null,
    status: "TODO",
    priority: 2,
    creator_id: 1,
    assigned_by_id: null,
    assignee_id: null,
    creator: { id: 1, username: "alice", role: "user" },
    assigned_by: null,
    assignee: null,
    project_id: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  mockedTasks.getStats.mockResolvedValue(emptyStats);
  mockedUsers.getUsers.mockResolvedValue([
    { id: 1, username: "alice", role: "user" },
    { id: 2, username: "bob", role: "user" },
  ]);
});

describe("Tasks page", () => {
  it("shows the empty state when there are no tasks", async () => {
    mockedTasks.getTasks.mockResolvedValue([]);

    render(<TasksPage />);

    expect(await screen.findByText("Задач не найдено")).toBeInTheDocument();
    expect(within(screen.getByRole("banner")).getByText("alice")).toBeInTheDocument();
  });

  it("renders the loaded tasks", async () => {
    mockedTasks.getTasks.mockResolvedValue([
      makeTask({ id: 1, title: "Купить молоко" }),
      makeTask({ id: 2, title: "Позвонить маме", priority: 3 }),
    ]);

    render(<TasksPage />);

    expect(await screen.findByText("Купить молоко")).toBeInTheDocument();
    expect(screen.getByText("Позвонить маме")).toBeInTheDocument();
  });

  it("creates a task and reloads the list", async () => {
    mockedTasks.getTasks.mockResolvedValueOnce([]).mockResolvedValue([
      makeTask({ id: 5, title: "Новая задача" }),
    ]);
    mockedTasks.createTask.mockResolvedValue(makeTask({ id: 5, title: "Новая задача" }));

    render(<TasksPage />);
    await screen.findByText("Задач не найдено");

    await userEvent.type(screen.getByPlaceholderText("Название задачи"), "Новая задача");
    await userEvent.click(screen.getByRole("button", { name: "Добавить" }));

    await waitFor(() =>
      expect(mockedTasks.createTask).toHaveBeenCalledWith({
        title: "Новая задача",
        description: null,
        priority: 2,
        assignee_id: null,
      }),
    );
    expect(await screen.findByText("Новая задача")).toBeInTheDocument();
  });

  it("changes a task status", async () => {
    mockedTasks.getTasks.mockResolvedValue([makeTask({ id: 1, title: "Купить молоко" })]);
    mockedTasks.updateTask.mockResolvedValue(makeTask({ id: 1, status: "DONE" }));

    render(<TasksPage />);
    const card = (await screen.findByText("Купить молоко")).closest("li")!;

    const statusSelect = within(card).getByRole("combobox");
    await userEvent.selectOptions(statusSelect, "DONE");

    await waitFor(() =>
      expect(mockedTasks.updateTask).toHaveBeenCalledWith(1, { status: "DONE" }),
    );
  });

  it("deletes a task after confirmation", async () => {
    mockedTasks.getTasks.mockResolvedValue([makeTask({ id: 1, title: "Купить молоко" })]);
    mockedTasks.deleteTask.mockResolvedValue(undefined);
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<TasksPage />);
    const card = (await screen.findByText("Купить молоко")).closest("li")!;

    await userEvent.click(within(card).getByRole("button", { name: "Удалить" }));

    await waitFor(() => expect(mockedTasks.deleteTask).toHaveBeenCalledWith(1));
  });

  it("does not delete when confirmation is cancelled", async () => {
    mockedTasks.getTasks.mockResolvedValue([makeTask({ id: 1, title: "Купить молоко" })]);
    vi.spyOn(window, "confirm").mockReturnValue(false);

    render(<TasksPage />);
    const card = (await screen.findByText("Купить молоко")).closest("li")!;

    await userEvent.click(within(card).getByRole("button", { name: "Удалить" }));

    expect(mockedTasks.deleteTask).not.toHaveBeenCalled();
  });

  it("shows an error when loading fails", async () => {
    mockedTasks.getTasks.mockRejectedValue(new Error("boom"));

    render(<TasksPage />);

    expect(await screen.findByText("Не удалось загрузить задачи")).toBeInTheDocument();
  });

  it("logs out when the logout button is clicked", async () => {
    mockedTasks.getTasks.mockResolvedValue([]);

    render(<TasksPage />);
    await screen.findByText("Задач не найдено");

    await userEvent.click(screen.getByRole("button", { name: "Выйти" }));
    expect(logout).toHaveBeenCalled();
  });
});
