from aiogram.filters.base import Filter
from aiogram.types import Message

from database import get_db, models


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        async for admin in get_db(models.Admin).find():
            if message.from_user.id == admin.get("user_id"):
                return True
        return False
