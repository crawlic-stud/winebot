from datetime import datetime

from aiogram import types
from aiogram.filters.callback_data import CallbackData
import pytz

from models import Event, Product


def create_edit_keyboard(
    state_names_mapping: dict[str, str],
    callback_data_class: type[CallbackData],
    row_len: int = 2,
):
    kb = []
    for i in range(0, len(state_names_mapping), row_len):
        slice = list(state_names_mapping.items())[i : row_len + i]
        row = []
        for state, text in slice:
            states_group, state_name = state.split(":")

            row.append(
                types.InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data_class(
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


async def send_event_info(
    m: types.Message,
    event: Event,
    markup: types.InlineKeyboardMarkup | None = None,
    edit: bool = False,
):
    text = (
        f"Название: {event.name}\n"
        f"Описание: {event.description}\n"
        f"Дата: {parse_dt_to_str(event.date)}\n"
        f"Цена: {event.price} руб.\n"
    )
    if edit:
        await m.delete()
    await m.answer_photo(
        event.image_id,
        text,
        reply_markup=markup,
    )


def get_message_from_update(
    update: types.Message | types.CallbackQuery,
) -> types.Message:
    if isinstance(update, types.Message):
        return update
    return update.message


def get_event_from_update(event: types.Update) -> types.Message | types.CallbackQuery:
    if event.message is not None:
        return event.message
    return event.callback_query


def parse_str_to_dt(dt_str: str):
    dt = datetime.strptime(dt_str, "%d.%m.%Y")
    return dt


def parse_dt_to_str(dt: datetime):
    return dt.strftime("%d.%m.%Y")


def get_moscow_datetime():
    dt = datetime.now(tz=pytz.timezone("Europe/Moscow"))
    return dt
