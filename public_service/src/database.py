from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    url=settings.DATABASE_URL, echo=False, pool_size=5, max_overflow=10
)

session_factory = async_sessionmaker(engine)


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        cols = []
        for ids, col in enumerate(self.__table__.columns.keys()):
            cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
