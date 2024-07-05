from fastapi import FastAPI


import uvicorn
from router import router as images_router


app = FastAPI()
app.include_router(router=images_router)


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8001)
