from aiogram import types

from handlers.delete import DeleteData


def back_button_row(callback_data: str) -> list[types.InlineKeyboardButton]:
    return [types.InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]


def delete_obj_row(obj_id: str, collection: str):
    return [
        types.InlineKeyboardButton(
            text="❌ Удалить",
            callback_data=DeleteData(object_id=obj_id, collection=collection).pack(),
        )
    ]
