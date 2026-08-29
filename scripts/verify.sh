#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/4] Docker Compose config"
docker compose config --quiet

echo "[2/4] Build image"
docker compose build

echo "[3/4] Compile Python"
docker compose run --rm --no-deps bot python -m compileall -q \
  bot.py config.py logging_config.py handlers providers services

echo "[4/4] Import providers"
docker compose run --rm --no-deps bot python -c \
  "from providers.mock import MockProvider; from providers.custom import CustomProvider; print('providers ok')"

echo "Verification complete"
