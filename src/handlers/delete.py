from aiogram import types, Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from bson import ObjectId

import database


CONFIRM_DELETE = "confirm_delete"
CANCEL_DELETE = "cancel_delete"


router = Router(name="delete")


class DeleteData(CallbackData, prefix="del"):
    object_id: str
    collection: str


@router.callback_query(DeleteData.filter())
async def send_are_you_sure_message(
    query: types.CallbackQuery, callback_data: DeleteData, state: FSMContext
):
    await query.message.delete()
    await state.update_data(callback_data.model_dump())
    obj = (
        await database.db[callback_data.collection].find_one(
            {"_id": ObjectId(callback_data.object_id)}
        )
        or {}
    )
    await query.message.answer(
        f'Уверены, что хотите удалить "{obj.get("name")}"?',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Да", callback_data=CONFIRM_DELETE)],
                [types.InlineKeyboardButton(text="Нет", callback_data=CANCEL_DELETE)],
            ]
        ),
    )


@router.callback_query(F.data == CONFIRM_DELETE)
async def delete_object(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await query.answer("Удаляем...")
    await database.remove_by_id_from_collection(data["collection"], data["object_id"])
    await query.message.delete()
    await query.message.answer("Успешно удалено. Вернуться в меню - /menu")


@router.callback_query(F.data == CANCEL_DELETE)
async def cancel_delete_object(query: types.CallbackQuery):
    await query.message.delete()
    await query.message.answer("Удаление отменено. Вернуться в меню - /menu")
