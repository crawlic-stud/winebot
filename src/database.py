import asyncio
import os
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient

import models

DB_NAME = os.environ["DB_NAME"]
MONGO_URL = f'mongodb://{os.environ["MONGO_USER"]}:{os.environ["MONGO_PASSWORD"]}@{os.environ["MONGO_HOST"]}:{os.environ["MONGO_PORT"]}'
client = AsyncIOMotorClient(MONGO_URL)
client.get_io_loop = asyncio.get_running_loop

db = client[DB_NAME]

database_map = {
    models.Product: db[models.Product.get_collection()],
    models.Event: db[models.Event.get_collection()],
    models.User: db[models.User.get_collection()],
    models.Admin: db[models.Admin.get_collection()],
}


def get_db(model: type[models.Model]):
    return database_map[model]


async def save(model: models.Model):
    db = get_db(model.__class__)
    await db.update_one(model.model_dump(), {"$set": model.model_dump()}, upsert=True)


async def get_by_id(_id: str, model_type: type[models.Model]) -> models.Model:
    raw_obj = await get_db(model_type).find_one({"_id": ObjectId(_id)})
    return model_type(**raw_obj)
