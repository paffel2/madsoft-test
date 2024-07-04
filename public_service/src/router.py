from fastapi import APIRouter, Query, UploadFile, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from queries import Memes
from schemas import MemeDescription
from config import settings
from typing import Annotated
import httpx
import base64
from sqlalchemy.ext.asyncio import AsyncSession
from database import session_factory
from exceptions import S3NotWorking


router = APIRouter(prefix="/memes")


async def get_session():
    try:
        session = session_factory()
        yield session
    finally:
        await session.close()


async def get_image_from_s3(meme_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.SERVICE_DOMAIN + "/images/",
                params={"meme_id": meme_id},
                headers={"token": settings.TOKEN},
            )
            if response.status_code != 200:
                raise S3NotWorking
            response_body = base64.b64encode(response.content).decode()
            content_type = response.headers.get("content-type")
            if not content_type:
                raise Exception

            return (response_body, content_type)
    except:
        raise S3NotWorking


async def add_image_to_s3(meme_id: int, image: UploadFile):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SERVICE_DOMAIN + "/images/",
                params={"meme_id": meme_id},
                files={"image": (image.filename, image.file, image.content_type)},
                headers={"token": settings.TOKEN},
            )
            if response.status_code != 201:
                raise S3NotWorking
    except:
        raise S3NotWorking


async def delete_image_from_s3(meme_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.SERVICE_DOMAIN + "/images/",
                params={"meme_id": meme_id},
                headers={"token": settings.TOKEN},
            )
            if response.status_code != 204:
                raise S3NotWorking
    except:
        raise S3NotWorking


@router.get("/")
async def get_memes_list(
    page: Annotated[int, Query(gt=0)] = 1, session: AsyncSession = Depends(get_session)
):
    result = await Memes.get_memes(session, page)
    return JSONResponse({"memes": jsonable_encoder(result)})


@router.get("/{meme_id}")
async def get_meme_by_id(meme_id: int, session: AsyncSession = Depends(get_session)):

    result = await Memes.get_meme_by_id(session, meme_id)
    response_body, content_type = await get_image_from_s3(meme_id)
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
            <img src="data:{content_type};base64,{response_body}">
            <h1>{result.name}</h1>
        </div>
    </body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)


@router.post("/")
async def add_meme(
    name: str, image: UploadFile, session: AsyncSession = Depends(get_session)
):
    try:
        result = await Memes.add_meme(session, name)
        await add_image_to_s3(result, image)
        await session.commit()
        return JSONResponse(
            {"status": "added", "link": f"{settings.DOMAIN_NAME}/memes/{result}"},
            status_code=201,
        )
    except:
        await session.rollback()
        raise


@router.put("/{meme_id}")
async def update_meme(
    meme_id: int,
    new_name: str | None = None,
    new_image: UploadFile | None = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        if new_name:
            await Memes.update_meme(session, meme_id, new_name)
        if new_image:
            await add_image_to_s3(meme_id, new_image)
        await session.commit()
        return JSONResponse(
            {"status": "updated", "link": f"{settings.DOMAIN_NAME}/memes/{meme_id}"},
            status_code=201,
        )
    except:
        await session.rollback()
        raise


@router.delete("/{meme_id}")
async def delete_meme(meme_id: int, session: AsyncSession = Depends(get_session)):
    try:
        await Memes.delete_meme(session, meme_id)
        await delete_image_from_s3(meme_id)
        await session.commit()
        return JSONResponse({"status": "deleted"})
    except:
        await session.rollback()
        raise
