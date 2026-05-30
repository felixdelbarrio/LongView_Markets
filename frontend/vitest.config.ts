import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: "./src/tests/setup.ts",
    globals: true,
    include: ["src/tests/**/*.test.ts", "src/tests/**/*.test.tsx"],
    exclude: ["src/tests/e2e/**", "node_modules/**", "dist/**"],
  },
});
