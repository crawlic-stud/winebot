from aiogram import types


def back_button_row(callback_data: str) -> list[types.InlineKeyboardButton]:
    return [types.InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]
