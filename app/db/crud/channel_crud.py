from sqlalchemy import select, delete
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Channel, UserChannel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from db.crud.schemas import AddChannelResult



import logging


logger = logging.getLogger(__name__)

async def add_user_channel(
    user_id: int,
    channel_id: int,
    channel_name: str,
    channel_username: str | None,
    channel_url: str,
    status: str,
    session: AsyncSession
) -> AddChannelResult:
    logger.info(f"[add_user_channel] Запущено добавление канала для пользователя {user_id}")
    logger.debug(f"[add_user_channel] Входные данные: channel_id={channel_id}, name={channel_name}, username={channel_username}, url={channel_url}, status={status}")

    try:
        user = await session.get(User, user_id)
        if not user:
            logger.warning(f"[add_user_channel] Пользователь с id={user_id} не найден.")
            return AddChannelResult.USER_NOT_FOUND

        existing_channel = await session.scalar(
            select(Channel).where(Channel.channel_id == channel_id)
        )

        if not existing_channel:
            logger.info(f"[add_user_channel] Канал не найден в базе. Добавляем новый канал: {channel_name}")
            new_channel = Channel(
                channel_id=channel_id,
                channel_name=channel_name,
                channel_username=channel_username,
                channel_url=channel_url,
                status=status
            )
            session.add(new_channel)
            await session.flush()
        else:
            logger.info(f"[add_user_channel] Канал с id={channel_id} уже существует. Проверяем необходимость обновления...")
            updated = False
            if (
                existing_channel.channel_name != channel_name
                or existing_channel.channel_username != channel_username
                or existing_channel.channel_url != channel_url
                or existing_channel.status != status
            ):
                logger.info(f"[add_user_channel] Обновляем данные канала: {channel_name}")
                existing_channel.channel_name = channel_name
                existing_channel.channel_username = channel_username
                existing_channel.channel_url = channel_url
                existing_channel.status = status
                updated = True

            if updated:
                await session.flush()

        
        stmt = (
            insert(UserChannel)
            .values(user_id=user_id, channel_id=channel_id)
            .on_conflict_do_nothing()
        )
        result = await session.execute(stmt)

        if result.rowcount > 0:
            logger.info(f"[add_user_channel] Связь пользователь-канал добавлена. Обновляем счётчик каналов пользователя.")
            user.count_channel += 1
            await session.commit()
            return AddChannelResult.SUCCESS

        logger.info(f"[add_user_channel] Связь уже существует. Завершаем без изменений.")
        await session.commit()
        return AddChannelResult.RELATION_EXISTS

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"[add_user_channel] IntegrityError: {e}")
        if "user_id" in str(e):
            return AddChannelResult.USER_NOT_FOUND
        return AddChannelResult.OTHER_ERROR

    except Exception as e:
        await session.rollback()
        logger.exception(f"[add_user_channel] Неизвестная ошибка: {e}")
        return AddChannelResult.OTHER_ERROR





async def get_user_channels(
    user_id: int,
    session: AsyncSession
) -> List[str]:
   
    stmt = select(UserChannel.channel_id).where(UserChannel.user_id == user_id)
    result = await session.execute(stmt)
    channel_ids = result.scalars().all()
    
    if not channel_ids:
        return []

    channels_stmt = select(Channel.channel_name).where(Channel.channel_id.in_(channel_ids))
    channels_result = await session.execute(channels_stmt)
    return channels_result.scalars().all()


async def remove_user_channel(
    user_id: int,
    channel_name: str,
    session: AsyncSession
) -> AddChannelResult:
    try:
        user = await session.get(User, user_id)
        if not user:
            return AddChannelResult.USER_NOT_FOUND

        channel = await session.scalar(
            select(Channel).where(Channel.channel_name == channel_name)
        )
        if not channel:
            return AddChannelResult.CHANNEL_NOT_FOUND

        stmt = (
            delete(UserChannel)
            .where(
                UserChannel.user_id == user_id,
                UserChannel.channel_id == channel.channel_id
            )
        )
        await session.execute(stmt)
        user.count_channel = max(0, user.count_channel - 1)

        users_left = await session.execute(
            select(UserChannel).where(UserChannel.channel_id == channel.channel_id)
        )

        if not users_left.scalars().first():
            await session.delete(channel)

        await session.commit()
        return AddChannelResult.SUCCESS

    except IntegrityError:
        await session.rollback()
        return AddChannelResult.OTHER_ERROR

    except Exception:
        await session.rollback()
        return AddChannelResult.OTHER_ERROR
