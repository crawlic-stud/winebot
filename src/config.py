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

logging.basicConfig(level=logging.INFO)


def setup():
    from handlers import product
    from handlers import user_view
    from handlers import delete

    dp.include_router(product.router)
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
                types.BotCommand(command="order", description="Создать новый товар"),
                *default_commands,
            ],
            types.BotCommandScopeChat(chat_id=admin["user_id"]),
        )


setup()
