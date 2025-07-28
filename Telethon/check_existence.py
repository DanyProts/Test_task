from telethon import TelegramClient
from core import settings
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel
from Telethon import ChannelAccessStatus


client = TelegramClient("my_session", int(settings.telethon_set.api_id), str(settings.telethon_set.api_hash))




async def check_channel_access(client: TelegramClient, channel_identifier: str) -> dict:
    """
    Проверяет, можно ли вступить в канал и читать сообщения.

    :param client: авторизованный TelegramClient
    :param channel_identifier: username (@...) или t.me/...
    :return: словарь с результатом проверки
    """
    result = {
        "status": ChannelAccessStatus.UNKNOWN_ERROR,
        "channel_id": None,
        "error": None
    }

    try:
        # Получение информации о сущности
        entity = await client.get_entity(channel_identifier)

        # Проверка, что это именно канал
        if not isinstance(entity, Channel):
            result["status"] = ChannelAccessStatus.NOT_A_CHANNEL
            result["error"] = "Указанный объект не является каналом."
            return result

        result["channel_id"] = entity.id

        # Попытка вступить в канал
        try:
            await client(JoinChannelRequest(entity))
        except Exception as e:
            result["status"] = ChannelAccessStatus.JOIN_ERROR
            result["error"] = f"Не удалось вступить в канал: {e}"
            return result

        # Попытка получить хотя бы одно сообщение
        try:
            messages = await client.get_messages(entity, limit=1)
            if messages:
                result["status"] = ChannelAccessStatus.SUCCESS
            else:
                result["status"] = ChannelAccessStatus.PARSE_ERROR
                result["error"] = "Нет сообщений для чтения."
        except Exception as e:
            result["status"] = ChannelAccessStatus.PARSE_ERROR
            result["error"] = f"Не удалось получить сообщения: {e}"

    except ValueError:
        result["status"] = ChannelAccessStatus.NOT_FOUND
        result["error"] = "Канал не найден"
    except Exception as e:
        result["status"] = ChannelAccessStatus.UNKNOWN_ERROR
        result["error"] = str(e)

    return result


