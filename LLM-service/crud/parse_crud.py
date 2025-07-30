import logging
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerChannel, Channel
from db import get_db, Channel
from core import settings
logger = logging.getLogger(__name__)


client = TelegramClient(
    "my_session",
    api_id=int(settings.telethon_set.api_id),
    api_hash=str(settings.telethon_set.api_hash),
    device_model="Pixel 7 Pro",
    system_version="Android 13",
    app_version="9.6.1",
    lang_code="ru",
)

async def track_channels(client: TelegramClient):
    """Мониторинг всех каналов из БД (статус public/private не проверяется)"""
    async for session in get_db():
        # Получаем ВСЕ каналы без проверки статуса
        query = session.query(Channel)
        result = await session.execute(query)
        channels = result.scalars().all()

        if not channels:
            logger.warning("В базе нет каналов для мониторинга")
            return

        entities = []
        for channel in channels:
            try:
                # Автоматическое преобразование ID (-100123 → 123)
                telethon_id = abs(channel.channel_id) - 1000000000000
                entity = await client.get_entity(
                    InputPeerChannel(
                        channel_id=telethon_id,
                        access_hash=0  # Не требуется, если клиент уже в канале
                    )
                )
                entities.append(entity)
                logger.info(f"✅ Успешно: {entity.title} (ID: {channel.channel_id})")
            except Exception as e:
                logger.error(f"❌ Ошибка: {channel.channel_name} (ID: {channel.channel_id}): {str(e)}")

        # Хэндлер новых сообщений
        @client.on(events.NewMessage(chats=entities))
        async def handler(event):
            chat = await event.get_chat()
            if event.message.text:
                logger.info(f"📩 {chat.title}: {event.message.text[:200]}...")

        logger.info(f"🔊 Запущен мониторинг {len(entities)} каналов")
        await client.run_until_disconnected()






