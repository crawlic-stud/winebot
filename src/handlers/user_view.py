from aiogram import types, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from bson import ObjectId

import database
import utils
import kb
from models import Admin, Product
from config import bot


VIEW_PRODUCTS = "view_products"
VIEW_EVENTS = "view_events"
GO_TO_MENU = "go_to_menu"
ORDER_PRODUCT = "order_product"
THANK_YOU_FOR_ORDER = "thx_bro"


class UserView(StatesGroup):
    products = State()
    product_detail = State()

    events = State()
    event_detail = State()


class OrderEvent(CallbackData, prefix="order_event"):
    event_id: str


class OrderProduct(CallbackData, prefix="order_product"):
    product_id: str


class ViewProduct(CallbackData, prefix="view_product"):
    product_id: str


router = Router(name="user_view")


async def get_all_products_kb():
    _kb = []
    async for raw_product in database.get_db(Product).find():
        product_id = str(raw_product["_id"])
        product = Product(**raw_product)
        _kb.append(
            [
                types.InlineKeyboardButton(
                    text=f"{product.name} - {product.price} руб.",
                    callback_data=ViewProduct(product_id=product_id).pack(),
                )
            ]
        )
    _kb.append(kb.back_button_row(GO_TO_MENU))
    return _kb


@router.callback_query(F.data == GO_TO_MENU)
@router.message(Command("menu", "start"))
async def send_menu(update: types.Message | types.CallbackQuery):
    text = "Выберите, что хотите приобрести:"
    reply_markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Вино", callback_data=VIEW_PRODUCTS)],
            [types.InlineKeyboardButton(text="Афиша", callback_data=VIEW_EVENTS)],
        ]
    )
    if isinstance(update, types.Message):
        await update.answer(text, reply_markup=reply_markup)
        return
    await update.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == VIEW_PRODUCTS)
async def view_products(query: types.CallbackQuery):
    await query.answer("Показываем...")
    text = "Список доступных товаров:"
    reply_markup = types.InlineKeyboardMarkup(
        inline_keyboard=await get_all_products_kb()
    )
    m = query.message
    if m.photo:
        await m.delete()
        await m.answer(text=text, reply_markup=reply_markup)
    else:
        await m.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(ViewProduct.filter())
async def view_product(query: types.CallbackQuery, callback_data: ViewProduct):
    await query.answer("Показываем")
    product: Product = await database.get_by_id(callback_data.product_id, Product)
    await utils.send_product_info(
        query.message,
        product,
        markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="❤️ Хочу! ❤️",
                        callback_data=OrderProduct(
                            product_id=callback_data.product_id
                        ).pack(),
                    )
                ],
                kb.back_button_row(VIEW_PRODUCTS),
            ]
        ),
        edit=True,
    )


@router.callback_query(F.data == THANK_YOU_FOR_ORDER)
async def say_thanks(query: types.CallbackQuery):
    await query.answer("Спасибо еще раз! С вами скоро свяжутся :)", show_alert=True)


@router.callback_query(OrderProduct.filter())
async def order_product(query: types.CallbackQuery, callback_data: OrderProduct):
    await query.answer(
        "Спасибо за заказ! Свяжемся с вами в ближайшее время :)", show_alert=True
    )
    product: Product = await database.get_by_id(callback_data.product_id, Product)
    text = (
        f"Поступила заявка!\n\n"
        f"Продукт: {product.name} {product.price} руб.\n"
        f"Покупатель: {query.from_user.full_name}\n"
        f"Ник в телеграме: @{query.from_user.username}"
    )
    await query.message.edit_reply_markup(
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Заказ принят 💚", callback_data=THANK_YOU_FOR_ORDER
                    )
                ],
                kb.back_button_row(VIEW_PRODUCTS),
            ]
        )
    )
    async for admin in database.get_db(Admin).find():
        await bot.send_message(admin["user_id"], text)
