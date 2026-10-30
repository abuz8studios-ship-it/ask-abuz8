#!/usr/bin/env bash
# Ask ABUZ8 — one-command judge/demo run (macOS/Linux).
#   ./start.sh [--fresh]
# --fresh deletes data/feed.runtime.json first for a pristine demo ledger.
set -u
cd "$(dirname "$0")"
PORT="${PORT:-8377}"

if [ "${1:-}" = "--fresh" ] && [ -f data/feed.runtime.json ]; then
  rm -f data/feed.runtime.json
  echo "[fresh] demo ledger reset."
fi

if [ ! -x .venv/bin/python ]; then
  echo "[setup] creating virtualenv..."
  python3 -m venv .venv || { echo "[setup] FAILED to create .venv"; exit 1; }
fi
echo "[setup] installing dependencies..."
.venv/bin/python -m pip install -q -r requirements.txt || { echo "[setup] pip install FAILED"; exit 1; }

echo "[run] starting MCP server on 127.0.0.1:${PORT}..."
.venv/bin/python mcp_server/server.py > server.log 2>&1 &
SRV=$!
cleanup() { kill "$SRV" 2>/dev/null; }
trap cleanup INT TERM

echo "[run] waiting for health check..."
for _ in $(seq 1 60); do
  if curl -s -m 2 "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "[run] server is UP (log: server.log, pid $SRV)."
    if [ "${ASK_ABUZ8_NO_BROWSER:-}" != "1" ]; then
      if command -v xdg-open >/dev/null; then xdg-open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 &
      elif command -v open >/dev/null; then open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 & fi
    fi
    echo "Ask ABUZ8 is running:  http://127.0.0.1:${PORT}/"
    echo "Press Ctrl+C to stop."
    wait "$SRV"
    exit 0
  fi
  sleep 1
done
echo "[run] server did not answer on port ${PORT} after 60s. See server.log."
kill "$SRV" 2>/dev/null
exit 1
