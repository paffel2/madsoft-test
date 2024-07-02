from pydantic import BaseModel


class MemeDescription(BaseModel):
    name: str
    link: str
