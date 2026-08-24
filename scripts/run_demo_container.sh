#!/bin/sh
set -eu

# L'appel app -> API reste HTTP, mais sur la boucle locale autorisee offline.
python -m uvicorn api.model.main:app --host 127.0.0.1 --port 8002 &
modele_pid=$!

cleanup() {
  kill "$modele_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
