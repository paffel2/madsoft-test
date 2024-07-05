from sqlalchemy import select, delete
from models import Meme
from config import settings
from exceptions import *
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import MemeDescription


class Memes:

    @staticmethod
    async def add_meme(session: AsyncSession, name: str):
        meme = Meme(
            name=name,
        )
        session.add(meme)

        await session.flush()
        await session.refresh(meme)
        return meme.id

    @staticmethod
    async def get_memes(session: AsyncSession, page: int = 1):

        query = (
            select(Meme)
            .order_by(Meme.id)
            .offset((page - 1) * settings.PAGE_SIZE)
            .limit(settings.PAGE_SIZE)
        )
        memes = await session.execute(query)
        result = memes.scalars().all()
        return [
            MemeDescription(
                name=meme.name, link=f"{settings.DOMAIN_NAME}/memes/{meme.id}"
            )
            for meme in result
        ]

    @staticmethod
    async def get_meme_by_id(session: AsyncSession, meme_id: int):
        query = select(Meme).where(Meme.id == meme_id)
        meme = await session.execute(query)
        result = meme.scalar_one_or_none()
        if result:
            return result
        else:
            raise MemeDoesntExist()

    @staticmethod
    async def update_meme(session: AsyncSession, meme_id: int, new_name: str):
        query = select(Meme).where(Meme.id == meme_id)
        result = await session.execute(query)
        meme = result.scalar_one_or_none()
        if meme:
            meme.name = new_name
            await session.flush()
            await session.refresh(meme)
            return meme
        else:
            raise MemeDoesntExist()

    @staticmethod
    async def delete_meme(session: AsyncSession, meme_id: int):
        query = delete(Meme).where(Meme.id == meme_id)
        result = await session.execute(query)
        if result.rowcount == 1:
            return None
        raise MemeDoesntExist()
