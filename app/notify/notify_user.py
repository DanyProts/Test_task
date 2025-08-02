from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import Chat
from db.models import User, UserChannel
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import logging
from typing import List
from text_batton import text_get

logger = logging.getLogger(__name__)

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

async def get_user_id(session: AsyncSession, chat: Chat) -> List[int]:
    stmt = (
        select(User.user_id)
        .join(UserChannel, User.user_id == UserChannel.user_id)
        .where(UserChannel.channel_id == chat.id)
    )
    result = await session.execute(stmt)
    return [row[0] for row in result.fetchall()]

async def notify_users_remove(
    user_ids: List[int],
    chat: Chat,
    bot: Bot,
) -> None:
    

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=text_get.t("notify.remove.channel", name= chat.title))
        except Exception as e:
            print(f"ERROR: {e}")