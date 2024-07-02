from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column


from database import Base


class Meme(Base):
    __tablename__ = "memes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
