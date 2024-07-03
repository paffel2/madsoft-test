from fastapi import APIRouter, Query, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from queries import Memes
from schemas import MemeDescription
from config import settings
from typing import Annotated
import httpx
import base64


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
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.SERVICE_DOMAIN + "/images/", params={"meme_id": meme_id}
        )
        response_result = base64.b64encode(response.content).decode()
        meme = MemeDescription(
            name=result.name, link=f"{settings.DOMAIN_NAME}/memes/{result.id}"
        )
        html_content = f"""<html>
    <head>
        <style>
        .image{{
            width:300px;
            height:300px;
            margin:auto;
            text-align:center;
            }}
            img{{
            width:100%;
            }}
        </style>
    </head>
    <body>
        <div class="image">
            <img src="data:image/jpg;base64,{response_result}">
            <h1>{result.name}</h1>
        </div>
    </body>
</html>
"""
        return HTMLResponse(content=html_content, status_code=200)


@router.post("/")
async def add_meme(name: str, image: UploadFile):
    result = await Memes.add_meme(name)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SERVICE_DOMAIN + "/images/",
            params={"meme_id": result},
            files={"image": (image.filename, image.file, image.content_type)},
        )
        return JSONResponse(
            {"status": "added", "link": f"{settings.DOMAIN_NAME}/memes/{result}"},
            status_code=201,
        )  # TODO добавить обработку ошибок


@router.put("/{meme_id}")
async def update_meme(
    meme_id: int,
    new_name: str | None = None,
    new_image: UploadFile | None = None,
):
    if new_name:
        await Memes.update_meme(meme_id, new_name)
    if new_image:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SERVICE_DOMAIN + "/images/",
                params={"meme_id": meme_id},
                files={
                    "image": (
                        new_image.filename,
                        new_image.file,
                        new_image.content_type,
                    )
                },
            )
    return JSONResponse(
        {"status": "updated", "link": f"{settings.DOMAIN_NAME}/memes/{meme_id}"},
        status_code=201,
    )


@router.delete("/{meme_id}")
async def delete_meme(meme_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            settings.SERVICE_DOMAIN + "/images/",
            params={"meme_id": meme_id},
        )
        await Memes.delete_meme(meme_id)

        return JSONResponse({"status": "deleted"})
