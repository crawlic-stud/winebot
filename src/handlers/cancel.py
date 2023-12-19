from aiogram import types, Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext


CANCEL_ACTION = "cancel"


router = Router(name="cancel")


@router.message(Command("cancel"))
async def cancel_any_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.reply("Отменил текущее действие!")
