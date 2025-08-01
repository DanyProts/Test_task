from sqlalchemy import select, delete
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Channel, UserChannel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from db.crud.schemas import AddChannelResult
import re



import logging


logger = logging.getLogger(__name__)

async def add_user_channel(session: AsyncSession, user_id: int, user_input: str) -> dict:
    
    CHANNEL_LINK_PATTERN = re.compile(r"^https://t\.me/[\w\d_+/=-]+$")
    user_input = user_input.strip()
    is_link = bool(CHANNEL_LINK_PATTERN.match(user_input))

    if is_link:
        stmt = select(Channel).where(Channel.channel_url == user_input)
    else:
        cleaned_input = user_input.replace("@", "")
        stmt = select(Channel).where(
            (Channel.channel_username.ilike(cleaned_input)) |
            (Channel.channel_name.ilike(f"%{cleaned_input}%"))
        )

    result = await session.execute(stmt)
    channel = result.scalar_one_or_none()

    if not channel:
        return {"status": "error", "message": "Канал не найден."}

    relation_stmt = select(UserChannel).where(
        (UserChannel.user_id == user_id) &
        (UserChannel.channel_id == channel.channel_id)
    )
    relation_result = await session.execute(relation_stmt)

    if relation_result.scalar_one_or_none():
        return {"status": "exists", "channel_name": channel.channel_name}

    new_relation = UserChannel(user_id=user_id, channel_id=channel.channel_id)
    session.add(new_relation)
    await session.commit()

    return {"status": "added", "channel_name": channel.channel_name}





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
    
async def get_users_by_channel(session: AsyncSession, channel_id: int) -> List[int]:
    try:
        result = await session.execute(
            select(UserChannel.user_id).where(UserChannel.channel_id == channel_id)
        )
        return [row[0] for row in result.all()]
    except Exception as e:
        print(f"Ошибка при поиске пользователей канала {channel_id}: {e}")
        return []