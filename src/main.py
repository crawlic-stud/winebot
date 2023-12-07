import asyncio

from config import dp, bot, ADMIN_ID
from database import get_db, models


async def main():
    await get_db(models.Admin).update_one(
        {"user_id": ADMIN_ID}, {"$set": {"user_id": ADMIN_ID}}, upsert=True
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
