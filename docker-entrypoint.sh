#!/usr/bin/env sh
set -e

# Ждём, пока база станет доступна (необязательно, но на всякий случай)
# можно установить pypi пакет wait-for-it или сделать ваш аналог

echo "Running Alembic migrations…"
alembic upgrade head

echo "Starting FastAPI…"
# Запускаем через python -m src, как у вас и задумано
exec python -m src
