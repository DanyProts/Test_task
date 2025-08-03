FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev make

# Сначала копируем только зависимости и README
COPY pyproject.toml poetry.lock README.md ./

# Установка poetry и зависимостей без установки проекта
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем всё остальное, включая core/
COPY . .

CMD ["python", "main.py"]
