from sqlalchemy import select, delete
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Channel, UserChannel, AddChannelResult
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError



async def add_user_channel(
    user_id: int,
    channel_name: str,
    session: AsyncSession
) -> AddChannelResult:
    
    try:
        
        user = await session.get(User, user_id)
        if not user:
            
            return AddChannelResult.USER_NOT_FOUND
        

        channel = await session.scalar(
            select(Channel)
            .where(Channel.channel_name == channel_name)
        )
        
        if not channel:
            
            channel = Channel(channel_name=channel_name)
            session.add(channel)
            await session.flush()
            
    
        stmt = (
            insert(UserChannel)
            .values(user_id=user_id, channel_id=channel.channel_id)
            .on_conflict_do_nothing()
        )
        result = await session.execute(stmt)

        if result.rowcount > 0:
            user.count_channel += 1
            await session.commit()
            return AddChannelResult.SUCCESS
        return AddChannelResult.RELATION_EXISTS
    
    except IntegrityError as e:
        await session.rollback()

        if "user_id" in str(e):
            return AddChannelResult.USER_NOT_FOUND
        return AddChannelResult.OTHER_ERROR
    
    except Exception as e:
        await session.rollback()
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
