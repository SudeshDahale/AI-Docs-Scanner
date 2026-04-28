from fastapi import FastAPI
from routes.upload import router

app = FastAPI()

app.include_router(router)