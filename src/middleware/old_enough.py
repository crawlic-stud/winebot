import logging
from typing import Any, Awaitable, Callable

from aiogram import types, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

from config import dp, old_enough_cache
from database import is_old_enough, get_db
from models import User
import utils


router = Router(name="old_enough")
logger = logging.getLogger("old")
ACCEPT_DATA = "i_am_old_enough"


class OldEnoughCheck(StatesGroup):
    accept = State()


@router.callback_query(F.data == ACCEPT_DATA)
async def accept_old_enough(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Звоним в паспортный стол...")
    user_id = query.from_user.id
    db = get_db(User)
    await db.update_one({"user_id": user_id}, {"$set": {"old_enough": True}})

    data = await state.get_data()
    handler = data.pop("_handler")
    event = data.pop("_event")
    handler_data = data.pop("_data")
    await query.message.delete()

    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    return await handler(event, handler_data)


@dp.update.outer_middleware()
async def check_is_old(
    handler: Callable[[types.Update, dict[str, Any]], Awaitable[Any]],
    event: types.Update,
    data: dict[str, Any],
) -> Awaitable:
    m_or_query = utils.get_event_from_update(event)
    message = utils.get_message_from_update(m_or_query)
    user_id = m_or_query.from_user.id
    state: FSMContext = data["state"]
    state_data = await state.get_data()
    current_state = await state.get_state()

    if current_state == "OldEnoughCheck:accept" and state_data.get("in_check"):
        return await handler(event, data)

    if user_id not in old_enough_cache:
        user_allowed = await is_old_enough(user_id)
        if user_allowed:
            old_enough_cache.add(user_id)
        else:
            await state.set_state(OldEnoughCheck.accept)
            await message.answer(
                "Вам уже есть 18 лет? Подтвердите, чтобы продолжить",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text="✅ Подтверждаю", callback_data=ACCEPT_DATA
                            )
                        ]
                    ]
                ),
            )
            await state.update_data(
                {"_handler": handler, "_event": event, "_data": data, "in_check": True}
            )
            ...
        return

    return await handler(event, data)
