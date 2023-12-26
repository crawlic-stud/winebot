import logging
import os

from motor.motor_asyncio import AsyncIOMotorCollection
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()
TG_TOKEN = os.environ["TG_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

bot = Bot(TG_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
active_users_cache = set()
old_enough_cache = set()

logging.basicConfig(level=logging.INFO)


def setup():
    import middleware.statistics
    from middleware import old_enough
    from handlers import cancel
    from handlers import product
    from handlers import events
    from handlers import admin_view
    from handlers import user_view
    from handlers import delete

    dp.include_router(old_enough.router)
    dp.include_router(cancel.router)
    dp.include_router(product.router)
    dp.include_router(events.router)
    dp.include_router(admin_view.router)
    dp.include_router(user_view.router)
    dp.include_router(delete.router)


async def on_startup(admins_db: AsyncIOMotorCollection):
    # setup default admin
    await admins_db.update_one(
        {"user_id": ADMIN_ID}, {"$set": {"user_id": ADMIN_ID}}, upsert=True
    )

    # setup commands
    default_commands = [
        types.BotCommand(command="start", description="Перезапустить бота"),
        types.BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(default_commands)
    async for admin in admins_db.find():
        await bot.set_my_commands(
            [
                types.BotCommand(command="admin", description="Админ-панель"),
                types.BotCommand(command="order", description="Создать новый товар"),
                types.BotCommand(command="event", description="Добавить в афишу"),
                types.BotCommand(command="cancel", description="Отменить заполнение"),
                *default_commands,
            ],
            types.BotCommandScopeChat(chat_id=admin["user_id"]),
        )


setup()
