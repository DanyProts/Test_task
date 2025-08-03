import httpx
import logging
from core import settings


logger = logging.getLogger(__name__)

async def review_post(post_text: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                str(settings.llm_server.url),
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

