from aiogram import types
from aiogram.filters.callback_data import CallbackData

from models import Product


class EditData(CallbackData, prefix="edit"):
    states_group: str
    state_name: str


def create_edit_keyboard(state_names_mapping: dict[str, str], row_len: int = 2):
    kb = []
    for i in range(0, len(state_names_mapping), row_len):
        slice = list(state_names_mapping.items())[i : row_len + i]
        row = []
        for state, text in slice:
            states_group, state_name = state.split(":")

            row.append(
                types.InlineKeyboardButton(
                    text=text,
                    callback_data=EditData(
                        states_group=states_group, state_name=state_name
                    ).pack(),
                )
            )
        kb.append(row)
    return kb


async def send_product_info(
    m: types.Message,
    product: Product,
    markup: types.InlineKeyboardMarkup | None = None,
    edit: bool = False,
):
    text = (
        f"Название: {product.name}\n"
        f"Описание: {product.description}\n"
        f"Цена: {product.price} руб.\n"
    )
    if edit:
        await m.delete()
    await m.answer_photo(
        product.image_id,
        text,
        reply_markup=markup,
    )


def get_message_from_update(
    update: types.Message | types.CallbackQuery,
) -> types.Message:
    if isinstance(update, types.Message):
        return update
    return update.message
