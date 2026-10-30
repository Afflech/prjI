import { rmSync } from "node:fs";

export default async function globalTeardown() {
  const databasePath = process.env.PLAYWRIGHT_E2E_DATABASE;
  if (!databasePath) return;

  for (const suffix of ["", "-shm", "-wal"]) {
    rmSync(`${databasePath}${suffix}`, { force: true });
  }
}
