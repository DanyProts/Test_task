# LLM Service

Этот микросервис реализует LLM-модель (или вызывает её через API) и предоставляет REST-интерфейс для анализа текстов, полученных из других сервисов (например, от Telegram-бота `app`).

---

## 🚀 Быстрый старт

### 📦 Требования

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 🔧 Установка и запуск

```bash
docker-compose up --build -d
