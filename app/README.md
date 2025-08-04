# Bot App Microservice

Этот микросервис отвечает за основную бизнес-логику проекта и взаимодействует с Telegram-ботом через библиотеку **Aiogram**. Он также обращается к внешнему LLM-сервису для анализа сообщений и работает с PostgreSQL-базой данных.

---

## 🚀 Быстрый старт

### 📦 Требования

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 🔧 Установка и запуск

```bash
docker-compose up --build -d
