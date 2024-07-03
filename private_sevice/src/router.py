from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse, Response
from s3 import client
import aiohttp


router = APIRouter(prefix="/images")


@router.post("/")
async def add_image(image: UploadFile, meme_id: int):
    try:
        await client.put_object(
            bucket_name="memes",
            object_name=str(meme_id),
            data=image,
            content_type=image.content_type,
            length=image.size,
        )

        return {"status": "image added"}
    except Exception as e:
        return JSONResponse({"error": "image not added"}, status_code=400)


@router.get("/")
async def get_image(meme_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            image = await client.get_object("memes", str(meme_id), session)
            file = await image.content.read()
            return Response(content=file, media_type=image.content_type)
    except Exception as e:
        return JSONResponse({"error": "image not found"}, status_code=400)


@router.delete("/")
async def delete_image(meme_id: int):
    try:
        await client.remove_object(bucket_name="memes", object_name=str(meme_id))
        return {"status": "image deleted"}
    except Exception as e:
        return JSONResponse({"error": "image not found"}, status_code=400)
