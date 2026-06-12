#!/usr/bin/env bash
# Start the stack and report the dashboard URL, whose host port is dynamic
# (docker picks the first free port in the 3000-3010 range).
# Extra args are passed to `docker compose up` (e.g. ./scripts/up.sh --build).
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose up -d "$@"

nginx_port=$(docker compose port dashboard 80 | head -n1 | awk -F: '{print $NF}')
echo
echo "  App (frontend + API):  http://localhost:5003"
echo "  Dashboard via nginx:   http://localhost:${nginx_port}"
echo
echo "Following logs (Ctrl+C detaches; the stack keeps running — stop it with 'docker compose down')"
docker compose logs -f
