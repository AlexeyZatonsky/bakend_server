# Dockerfile

# 1. Базовый образ с Python
FROM python:3.11-slim

# 2. Рабочая директория в контейнере
WORKDIR /app

# 3. Копируем только зависимости для их установки
COPY requirements.txt .

# 4. Устанавливаем system-зависимости (если нужны) и Python-библиотеки
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y --auto-remove gcc

# 5. Копируем весь исходный код
COPY . .

# 6. Копируем скрипт-инициализатор
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 7. Точка входа — сначала миграции, потом приложение
ENTRYPOINT ["docker-entrypoint.sh"]
