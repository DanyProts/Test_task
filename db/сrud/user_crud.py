from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User

async def get_or_create_user(user_id: int, first_name: str, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            user_id=user_id,
            first_name=first_name,
            is_active=True,
            count_channel=0,
            role="client"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user

async def change_active_status(user_id: int, session: AsyncSession) -> bool:
    result = await session.execute(
        select(User).where(User.user_id == user_id)  
    )
    user = result.scalar_one_or_none()               

    if user is None:                                 
        return False

    user.is_active = not user.is_active             
    await session.commit()                           
    return True
