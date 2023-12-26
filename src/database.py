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
    models.UserStat: db[models.UserStat.get_collection()],
}


def get_db(model: type[models.Model]):
    return database_map[model]


async def save(model: models.Model):
    db = get_db(model.__class__)
    id_filter = {"_id": ObjectId(model.id)}
    exists = await db.find_one(id_filter)
    if not exists:
        await db.insert_one(model.model_dump(exclude={"id"}))
    else:
        await db.update_one(id_filter, {"$set": model.model_dump(exclude={"id"})})


async def get_by_id(_id: str, model_type: type[models.Model]) -> models.Model:
    raw_obj = await get_db(model_type).find_one({"_id": ObjectId(_id)})
    return model_type(**raw_obj)


async def is_admin(user_id: int):
    return bool(await get_db(models.Admin).find_one({"user_id": user_id}))


async def is_old_enough(user_id: int):
    user = (await get_db(models.User).find_one({"user_id": user_id})) or {}
    return user.get("old_enough", False)


async def remove_by_id_from_collection(collection: str, _id: str):
    obj_id = ObjectId(_id)
    await db[collection].delete_one({"_id": obj_id})
