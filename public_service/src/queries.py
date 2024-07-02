from sqlalchemy import select, delete
from models import Meme
from database import session_factory
from config import settings
from exceptions import *


class Memes:

    @staticmethod
    async def add_meme(name: str):
        async with session_factory() as session:

            meme = Meme(
                name=name,
            )
            session.add(meme)

            await session.flush()
            await session.commit()
            await session.refresh(meme)
            return meme.id

    @staticmethod
    async def get_memes(page: int = 1):
        async with session_factory() as session:

            query = (
                select(Meme)
                .order_by(Meme.id)
                .offset((page - 1) * settings.PAGE_SIZE)
                .limit(settings.PAGE_SIZE)
            )
            memes = await session.execute(query)
            return memes.scalars().all()

    @staticmethod
    async def get_meme_by_id(meme_id: int):
        async with session_factory() as session:

            query = select(Meme).where(Meme.id == meme_id)
            meme = await session.execute(query)
            result = meme.scalar_one_or_none()
            if result:
                return result
            else:
                raise MemeDoesntExist()

    @staticmethod
    async def update_meme(meme_id: int, new_name: str):
        async with session_factory() as session:
            query = select(Meme).where(Meme.id == meme_id)
            result = await session.execute(query)
            meme = result.scalar_one_or_none()
            if meme:
                meme.name = new_name
                await session.flush()
                await session.commit()
                await session.refresh(meme)
                return meme
            else:
                raise MemeDoesntExist()

    @staticmethod
    async def delete_meme(meme_id: int):
        async with session_factory() as session:
            query = delete(Meme).where(Meme.id == meme_id)
            result = await session.execute(query)
            await session.commit()
            if result.rowcount == 1:
                return None
            raise MemeDoesntExist()
