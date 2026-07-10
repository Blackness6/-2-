import { defineConfig } from "vitest/config";
import { loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  // Куда dev-сервер проксирует запросы к бэку.
  // docker-compose пробрасывает api на 8001; локальный uvicorn — на 8000.
  const backend = env.VITE_BACKEND_URL || "http://localhost:8001";

  return {
    plugins: [react()],

    server: {
      host: true,
      port: 3000,
      proxy: {
        "/api": { target: backend, changeOrigin: true },
        "/auth": { target: backend, changeOrigin: true },
      },
    },

    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./src/setupTests.ts",
    },
  };
});