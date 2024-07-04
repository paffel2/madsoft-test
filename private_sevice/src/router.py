from fastapi import APIRouter, HTTPException, UploadFile, Depends, Header, status
from fastapi.responses import JSONResponse, Response
from s3 import client
import aiohttp
from typing import Annotated
from config import settings


router = APIRouter(prefix="/images")


async def check_token(token: Annotated[str, Header()]):
    if token != settings.TOKEN:
        raise HTTPException(status_code=401)


@router.post("/")
async def add_image(
    image: UploadFile,
    meme_id: int,
    dependency=Depends(check_token),
):
    try:
        await client.put_object(
            bucket_name="memes",
            object_name=str(meme_id),
            data=image,
            content_type=image.content_type,
            length=image.size,
        )

        return JSONResponse({"status": "image added"}, status_code=201)
    except Exception as e:
        return JSONResponse({"error": "image not added"}, status_code=400)


@router.get("/")
async def get_image(
    meme_id: int,
    dependency=Depends(check_token),
):
    try:
        async with aiohttp.ClientSession() as session:
            image = await client.get_object("memes", str(meme_id), session)
            file = await image.content.read()
            return Response(content=file, media_type=image.content_type)
    except Exception as e:
        return JSONResponse({"error": "image not found"}, status_code=400)


@router.delete("/")
async def delete_image(
    meme_id: int,
    dependency=Depends(check_token),
):
    try:
        await client.remove_object(bucket_name="memes", object_name=str(meme_id))
        return Response(status_code=204)
    except Exception as e:
        return JSONResponse({"error": "image not found"}, status_code=400)
