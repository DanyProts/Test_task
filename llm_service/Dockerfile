FROM python:3.11-alpine

WORKDIR /app


RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev make

COPY pyproject.toml poetry.lock README.md* ./


RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root


COPY . .


CMD ["python", "main.py"]
