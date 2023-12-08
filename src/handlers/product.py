from typing import Any
from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from filters.admin_filter import AdminFilter
from models import Product
import database
import utils


SAVE_ORDER = "save_order"


class CreateOrder(StatesGroup):
    name = State()
    photo = State()
    description = State()
    price = State()
    final = State()


EDIT_PRODUCT_BUTTONS = [
    [
        types.InlineKeyboardButton(
            text="✅ Сохранить",
            callback_data=SAVE_ORDER,
        )
    ],
    *utils.create_edit_keyboard(
        {
            CreateOrder.name.state: "✏️ Название",
            CreateOrder.photo.state: "✏️ Фото",
            CreateOrder.description.state: "✏️ Описание",
            CreateOrder.price.state: "✏️ Цена",
        }
    ),
]


router = Router(
    name="product",
)


async def send_final_message(m: types.Message, product: Product):
    await utils.send_product_info(
        m=m,
        product=product,
        markup=types.InlineKeyboardMarkup(inline_keyboard=EDIT_PRODUCT_BUTTONS),
    )


async def handle_edit(data: dict[str, Any], context: FSMContext, m: types.Message):
    is_edit = data.get("edit")
    if is_edit:
        await m.reply("Изменено!")
        await send_final_message(m, Product(**data))
        await context.set_state(CreateOrder.final)
    return is_edit


@router.message(Command("order"), AdminFilter())
async def create_order(m: types.Message, state: FSMContext):
    await m.reply("Введите название продукта, который хотите добавить:")
    await state.set_state(CreateOrder.name)


@router.message(CreateOrder.name)
async def add_name(m: types.Message, state: FSMContext):
    data = await state.update_data(name=m.text)
    is_edit = await handle_edit(data, state, m)
    if not is_edit:
        await m.reply("Имя добавлено! Прикрепите фотографию продукта:")
        await state.set_state(CreateOrder.photo)


@router.message(CreateOrder.photo)
async def attach_photo(m: types.Message, state: FSMContext):
    if not m.photo:
        await m.reply("Прикрепите фотографию!")
        return
    data = await state.update_data(image_id=m.photo[-1].file_id)
    is_edit = await handle_edit(data, state, m)
    if not is_edit:
        await m.reply("Фото добавлено! Напишите описание продукта:")
        await state.set_state(CreateOrder.description)


@router.message(CreateOrder.description)
async def add_description(m: types.Message, state: FSMContext):
    data = await state.update_data(description=m.text)
    is_edit = await handle_edit(data, state, m)
    if not is_edit:
        await m.reply("Описание добавлено! Напишите цену продукта в рублях:")
        await state.set_state(CreateOrder.price)


@router.message(CreateOrder.price)
async def add_price(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        await m.reply("Введите число!")
        return
    data = await state.update_data(price=float(m.text))
    product = Product(**data)
    await send_final_message(m, product)


@router.callback_query(utils.EditData.filter())
async def edit_text_field(
    query: types.CallbackQuery, callback_data: utils.EditData, state: FSMContext
):
    await query.answer("Редактируем...")
    await state.update_data(edit=True)
    m = query.message
    if callback_data.state_name == "name":
        await m.answer("Укажите новое название:")
        await state.set_state(CreateOrder.name)
    elif callback_data.state_name == "photo":
        await m.answer("Отправьте новое фото:")
        await state.set_state(CreateOrder.photo)
    elif callback_data.state_name == "description":
        await m.answer("Отправьте новое описание:")
        await state.set_state(CreateOrder.description)
    elif callback_data.state_name == "price":
        await m.answer("Отправьте новую цену в рублях:")
        await state.set_state(CreateOrder.price)


@router.callback_query(F.data == SAVE_ORDER)
async def save_order(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Сохраняем...")
    data = await state.get_data()
    product = Product(**data)
    await database.save(product)
    await state.clear()
    await query.message.delete_reply_markup()
    await query.message.answer(
        "Сохранено! Можете просмотреть или отредактировать товар по команде /menu"
    )
