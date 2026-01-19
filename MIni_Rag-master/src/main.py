from fastapi import FastAPI
from routes import base, data
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongo.connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db.client = app.mongo.connection[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown():
    app.mongo.connection.close()

app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)
