import { defineConfig } from "playwright/test";
import { existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDir = dirname(fileURLToPath(import.meta.url));
const repoDir = resolve(frontendDir, "..");
const backendDir = join(repoDir, "backend");
const backendPort = Number(process.env.E2E_BACKEND_PORT || 8011);
const frontendPort = Number(process.env.E2E_FRONTEND_PORT || 4173);
const backendUrl = `http://127.0.0.1:${backendPort}`;
const frontendUrl = `http://127.0.0.1:${frontendPort}`;
const databasePath = join(tmpdir(), `mini-notebooklm-e2e-${process.pid}.sqlite3`);
const virtualenvPython = join(repoDir, ".venv", "bin", "python");
const python = process.env.E2E_PYTHON ||
  (existsSync(virtualenvPython) ? virtualenvPython : "python3");

for (const suffix of ["", "-shm", "-wal"]) {
  rmSync(`${databasePath}${suffix}`, { force: true });
}
process.env.PLAYWRIGHT_E2E_DATABASE = databasePath;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  outputDir: "./test-results",
  globalTeardown: "./e2e/global-teardown.js",
  use: {
    baseURL: frontendUrl,
    browserName: "chromium",
    headless: true,
    viewport: { width: 1440, height: 1000 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: `"${python}" -m uvicorn app.main:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: backendDir,
      url: `${backendUrl}/health`,
      timeout: 60_000,
      reuseExistingServer: false,
      stdout: "ignore",
      stderr: "pipe",
      env: {
        PYTHONPATH: backendDir,
        NOTEBOOKLM_DB_PATH: databasePath,
        EMBEDDING_PROVIDER: "hash",
      },
    },
    {
      command: `npm run dev -- --port ${frontendPort} --strictPort`,
      cwd: frontendDir,
      url: frontendUrl,
      timeout: 60_000,
      reuseExistingServer: false,
      stdout: "ignore",
      stderr: "pipe",
      env: { BACKEND_URL: backendUrl },
    },
  ],
});
