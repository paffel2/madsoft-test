from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from queries import Memes
from schemas import MemeDescription
from config import settings
from typing import Annotated


router = APIRouter(prefix="/memes")


@router.get("/")
async def get_memes_list(page: Annotated[int, Query(gt=0)] = 1):
    result = await Memes.get_memes(page)
    list_of_memes = [
        MemeDescription(name=meme.name, link=f"{settings.DOMAIN_NAME}/memes/{meme.id}")
        for meme in result
    ]
    return JSONResponse({"memes": jsonable_encoder(list_of_memes)})


@router.get("/{meme_id}")
async def get_meme_by_id(meme_id: int):
    result = await Memes.get_meme_by_id(meme_id)
    meme = MemeDescription(
        name=result.name, link=f"{settings.DOMAIN_NAME}/memes/{result.id}"
    )
    return JSONResponse({"name": jsonable_encoder(meme)})


@router.post("/")
async def add_meme(name: str):
    result = await Memes.add_meme(name)
    return JSONResponse(
        {"status": "added", "link": f"{settings.DOMAIN_NAME}/memes/{result}"},
        status_code=201,
    )


@router.put("/{meme_id}")
async def update_meme(meme_id: int, new_name: str):
    result = await Memes.update_meme(meme_id, new_name)
    return JSONResponse(
        {"status": "updated", "link": f"{settings.DOMAIN_NAME}/memes/{result.id}"},
        status_code=201,
    )


@router.delete("/{meme_id}")
async def delete_meme(meme_id: int):
    await Memes.delete_meme(meme_id)
    return JSONResponse({"status": "deleted"})
