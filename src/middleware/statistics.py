import asyncio
import logging
from typing import Any, Awaitable, Callable

from aiogram import types
import bson
from motor.motor_asyncio import AsyncIOMotorCollection

from config import dp, active_users_cache
from database import get_db
from models import User, UserStat
import utils

logger = logging.getLogger("stat")


def get_event_from_update(event: types.Update) -> types.Message | types.CallbackQuery:
    if event.message is not None:
        return event.message
    return event.callback_query


async def update_daily_stat(user_id: int, db: AsyncIOMotorCollection):
    d = utils.get_moscow_datetime().date().strftime("%d/%m/%Y")
    await db.update_one(
        {"d": d}, {"$set": {"d": d}, "$addToSet": {"users": user_id}}, upsert=True
    )


@dp.update.outer_middleware()
async def add_active_users(
    handler: Callable[[types.Update, dict[str, Any]], Awaitable[Any]],
    event: types.Update,
    data: dict[str, Any],
) -> Awaitable:
    message_or_query = get_event_from_update(event)
    user = message_or_query.from_user
    user_id = user.id
    db = get_db(User)
    id_filter = {"user_id": user_id}
    logger.info(f"Adding active user: {user.username}")

    # update today active users
    asyncio.create_task(update_daily_stat(user_id, get_db(UserStat)))

    # update last time user been active
    if user_id in active_users_cache:
        asyncio.create_task(
            db.update_one(
                id_filter, {"$set": {"last_active": utils.get_moscow_datetime()}}
            )
        )
        return await handler(event, data)

    asyncio.create_task(
        db.update_one(
            id_filter,
            {
                "$set": User(
                    user_id=user_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    last_active=utils.get_moscow_datetime(),
                ).model_dump(exclude={"object_id", "id"})
            },
            upsert=True,
        )
    )
    return await handler(event, data)
