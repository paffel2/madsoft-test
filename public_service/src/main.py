from fastapi import FastAPI
from fastapi.responses import JSONResponse
from exceptions import *


import uvicorn
from router import router as meme_router


app = FastAPI()
app.include_router(router=meme_router)


@app.exception_handler(MemeDoesntExist)
async def meme_doesnt_exist(request, exc):
    return JSONResponse(
        {"message": "error", "content": "meme doesn't exist"},
        status_code=400,
    )


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
