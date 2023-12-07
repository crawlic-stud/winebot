import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()
TG_TOKEN = os.environ["TG_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

bot = Bot(TG_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)


def setup():
    # create base admin

    from handlers import product
    from handlers import user_view

    dp.include_router(product.router)
    dp.include_router(user_view.router)


setup()
