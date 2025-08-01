import httpx
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import logging
from typing import List

logger = logging.getLogger(__name__)

async def review_post(post_text: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://localhost:8001/channel_check",
                json={"channel_identifier": post_text}
            )
            response.raise_for_status()
            logger.info(f"Запрос на проверку поста успешно выполнен: {post_text}")
            json_response = response.json()
            return json_response.get("text", "⚠️ Ошибка: пустой ответ от модели.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка сервера при проверке поста: {e.response.status_code}")
        return {"access_status": "ERROR", "error": f"Ошибка сервера: {e.response.status_code}"}
    except httpx.RequestError as e:
        logger.error(f"Сетевой сбой при проверке поста: {e}")
        return {"access_status": "ERROR", "error": f"Сетевой сбой: {str(e)}"}

async def send_bulk_message(bot: Bot, user_ids: List[int], text: str) -> None:
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            logger.info(f"Сообщение успешно отправлено пользователю {user_id}")
        except TelegramForbiddenError:
            logger.warning(f"Бот заблокирован пользователем {user_id} или нет разрешения писать.")
        except TelegramBadRequest as e:
            logger.warning(f"Ошибка TelegramBadRequest при отправке {user_id}: {e}")
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при отправке пользователю {user_id}: {e}")