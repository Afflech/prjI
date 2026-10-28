#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  echo "Chưa tìm thấy virtualenv tại $ROOT_DIR/.venv" >&2
  echo "Khởi tạo bằng: python3 -m venv .venv && .venv/bin/python -m pip install -r backend/requirements.txt" >&2
  exit 1
fi

exec "$PYTHON" -m uvicorn app.main:app \
  --reload \
  --port "${PORT:-8000}" \
  --app-dir "$ROOT_DIR/backend"
