from miniopy_async import Minio
from config import settings
import asyncio

client = Minio(
    endpoint=settings.S3_ENDPOINT,
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    secure=False,
)


async def create_bucket():
    is_exist = await client.bucket_exists("memes")
    if not is_exist:
        await client.make_bucket("memes")


loop = asyncio.get_event_loop()
loop.run_until_complete(create_bucket())
loop.close()
