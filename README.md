# 🧠 Telegram Bot + LLM Microservices Project

Этот проект представляет собой систему из двух микросервисов:

1. **Bot App** — микросервис Telegram-бота на `Aiogram`, обрабатывает пользователей, сохраняет данные и обращается к LLM-сервису.
2. **LLM Service** — микросервис на `FastAPI`, реализующий обработку и анализ текста с помощью модели (или внешнего API).

---

## 🧱 Архитектура

![alt text](image.png)

---

## 🚀 Запуск проекта

### 📦 Требования

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 🔧 Шаги

1. Клонируй репозиторий:
   ```bash
   git clone https://github.com/DanyProts/Test_task.git
   cd your_project

2. Создай файл .env в корне проекта с такими переменными:
    # Подключение к PostgreSQL (временно на локальном хосте)
    DB__URL=postgresql+asyncpg://postgres:111111@host.docker.internal:5432/test_task

    # Telegram bot
    BOT_TOKEN=your_telegram_bot_token

    # URL для llm_service
    LLM_SERVER__URL=http://llm_service:8001/your_prefix
3. Запусти всё:
    ```bash
    docker-compose up --build -d
4. Остановить работу:
    ```bash
    docker-compose down
5. Запустить повторно:
    ```bash
    docker-compose up -d
