import { describe, it, expect, vi, beforeEach } from "vitest";
import * as taskApi from "./taskApi";
import { api } from "./client";
import type { Task } from "../types/task";

vi.mock("./client", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

const sampleTask: Task = {
  id: 1,
  title: "Test",
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
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("tasks api", () => {
  it("getTasks passes filters as params and returns data", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: [sampleTask] });

    const result = await taskApi.getTasks({ status: "TODO", priority: 2 });

    expect(mockedApi.get).toHaveBeenCalledWith("/api/tasks", {
      params: { status: "TODO", priority: 2 },
    });
    expect(result).toEqual([sampleTask]);
  });

  it("getStats returns stats data", async () => {
    const stats = { TODO: 1, IN_PROGRESS: 0, DONE: 0, CANCELLED: 0 };
    mockedApi.get.mockResolvedValueOnce({ data: stats });

    const result = await taskApi.getStats();

    expect(mockedApi.get).toHaveBeenCalledWith("/api/tasks/stats");
    expect(result).toEqual(stats);
  });

  it("createTask posts payload and returns created task", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: sampleTask });

    const result = await taskApi.createTask({ title: "Test", priority: 2 });

    expect(mockedApi.post).toHaveBeenCalledWith("/api/tasks", {
      title: "Test",
      priority: 2,
    });
    expect(result).toEqual(sampleTask);
  });

  it("updateTask patches the correct id", async () => {
    const updated = { ...sampleTask, status: "DONE" as const };
    mockedApi.patch.mockResolvedValueOnce({ data: updated });

    const result = await taskApi.updateTask(1, { status: "DONE" });

    expect(mockedApi.patch).toHaveBeenCalledWith("/api/tasks/1", { status: "DONE" });
    expect(result).toEqual(updated);
  });

  it("deleteTask calls delete on the correct id", async () => {
    mockedApi.delete.mockResolvedValueOnce({ data: undefined });

    await taskApi.deleteTask(1);

    expect(mockedApi.delete).toHaveBeenCalledWith("/api/tasks/1");
  });
});
