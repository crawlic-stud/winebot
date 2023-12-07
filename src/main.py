import asyncio

from config import dp, bot, ADMIN_ID, on_startup
from database import get_db, models


async def main():
    admins_db = get_db(models.Admin)
    await on_startup(admins_db)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
