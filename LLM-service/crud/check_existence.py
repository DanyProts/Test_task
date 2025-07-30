from telethon import TelegramClient
from core import settings
import logging
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel
from .schemas import ChannelAccessStatus
import re
from telethon.errors import UserAlreadyParticipantError

client = TelegramClient("my_session", int(settings.telethon_set.api_id), str(settings.telethon_set.api_hash))



async def check_channel_access(client: TelegramClient, channel_identifier: str) -> dict:
    result = {
        "access_status": ChannelAccessStatus.UNKNOWN_ERROR,
        "channel_id": None,
        "channel_name": None,
        "channel_username": None,
        "channel_url": None,
        "channel_status": None,  
        "error": None
    }

    logging.info(f"Проверка канала по идентификатору: {channel_identifier}")

    try:
        private_match = re.match(r"^https://t\.me/(?:\+|joinchat/)([\w-]+)$", channel_identifier)

        if private_match:
            invite_hash = private_match.group(1)
            logging.info(f"Выявлен приватный канал. Хеш приглашения: {invite_hash}")

            try:
                update = await client(ImportChatInviteRequest(invite_hash))
                entity = update.chats[0]
                logging.info(f"Успешно подключились к приватному каналу: {entity.title}")
                result["channel_status"] = "private"
                result["channel_url"] = channel_identifier

            except UserAlreadyParticipantError:
                logging.info("Пользователь уже является участником приватного канала. Получаем entity...")
                entity = await client.get_entity(channel_identifier)
                result["channel_status"] = "private"
                result["channel_url"] = channel_identifier

            except Exception as e:
                logging.error(f"Ошибка подключения к приватному каналу: {e}")
                result["access_status"] = ChannelAccessStatus.JOIN_ERROR
                result["error"] = f"Ошибка подключения к приватному каналу: {e}"
                return result

        else:
            logging.info("Проверка как публичного канала...")
            entity = await client.get_entity(channel_identifier)
            result["channel_status"] = "public"
            result["channel_url"] = f"https://t.me/{entity.username}" if entity.username else None
            result["channel_username"] = entity.username

        if not isinstance(entity, Channel):
            logging.warning("Указанный объект не является каналом.")
            result["access_status"] = ChannelAccessStatus.NOT_A_CHANNEL
            result["error"] = "Указанный объект не является каналом."
            return result

        # Исправлено: гарантированно возвращаем ID с префиксом -100 для каналов
        channel_id = entity.id
        if isinstance(entity, Channel) and not str(channel_id).startswith('-100'):
            channel_id = int(f"-100{channel_id}")
            
        result["channel_id"] = channel_id
        result["channel_name"] = entity.title

        logging.info(f"Канал получен: {entity.title} (ID: {channel_id})")

        try:
            await client(JoinChannelRequest(entity))
            logging.info("Вступление в канал успешно или уже в нём.")
        except Exception as e:
            logging.warning(f"Ошибка вступления в канал: {e}")
            result["access_status"] = ChannelAccessStatus.JOIN_ERROR
            result["error"] = f"Не удалось вступить в канал: {e}"
            return result

        try:
            messages = await client.get_messages(entity, limit=1)
            if messages:
                logging.info("Сообщения успешно получены. Доступ к каналу подтверждён.")
                result["access_status"] = ChannelAccessStatus.SUCCESS
            else:
                logging.warning("Канал пуст. Нет сообщений для чтения.")
                result["access_status"] = ChannelAccessStatus.PARSE_ERROR
                result["error"] = "Нет сообщений для чтения."
        except Exception as e:
            logging.error(f"Не удалось получить сообщения: {e}")
            result["access_status"] = ChannelAccessStatus.PARSE_ERROR
            result["error"] = f"Не удалось получить сообщения: {e}"

    except ValueError:
        logging.warning("Канал не найден.")
        result["access_status"] = ChannelAccessStatus.NOT_FOUND
        result["error"] = "Канал не найден"
    except Exception as e:
        logging.exception("Произошла неизвестная ошибка:")
        result["access_status"] = ChannelAccessStatus.UNKNOWN_ERROR
        result["error"] = str(e)

    return result







