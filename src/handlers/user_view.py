from aiogram import types, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

import database
import utils
import kb
from models import Admin, Event, Product
from config import bot


VIEW_PRODUCTS = "view_products"
ORDER_PRODUCT = "order_product"
THANK_YOU_FOR_ORDER = "thx_bro"
VIEW_EVENTS = "view_events"
I_WILL_GO = "i_will_go"
GO_TO_MENU = "go_to_menu"


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


class ViewEvent(CallbackData, prefix="view_event"):
    event_id: str


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


async def get_all_events_kb():
    _kb = []
    async for raw_event in database.get_db(Event).find():
        event_id = str(raw_event["_id"])
        event = Event(**raw_event)
        _kb.append(
            [
                types.InlineKeyboardButton(
                    text=f"{event.name} - {utils.parse_dt_to_str(event.date)}",
                    callback_data=ViewEvent(event_id=event_id).pack(),
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
    async for p in database.get_db(Product).find():
        product = Product(**p)
        await utils.send_product_info(
            query.message,
            product,
            markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="❤️ Заказать! ❤️",
                            callback_data=OrderProduct(product_id=str(p["_id"])).pack(),
                        )
                    ],
                ]
            ),
        )

    await query.message.answer(
        "Выбирайте!",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Связаться с админом", url="https://t.me/pen_np"
                    )
                ],
                kb.back_button_row(GO_TO_MENU),
            ]
        ),
    )


@router.callback_query(F.data == VIEW_EVENTS)
async def view_events(query: types.CallbackQuery):
    await query.answer("Показываем...")
    text = "Список доступных товаров:"
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=await get_all_events_kb())
    m = query.message
    if m.photo:
        await m.delete()
        await m.answer(text=text, reply_markup=reply_markup)
    else:
        await m.edit_text(text=text, reply_markup=reply_markup)


async def render_event_view_for_user(
    query: types.CallbackQuery, object_id: str, event: Event
):
    await utils.send_event_info(
        query.message,
        event,
        markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="❤️ Хочу пойти! ❤️",
                        callback_data=OrderEvent(event_id=object_id).pack(),
                    )
                ],
                kb.back_button_row(VIEW_EVENTS),
            ]
        ),
        edit=True,
    )


@router.callback_query(ViewEvent.filter())
async def view_event(
    query: types.CallbackQuery, callback_data: ViewEvent, state: FSMContext
):
    await query.answer("Показываем")
    event: Event = await database.get_by_id(callback_data.event_id, Event)
    await render_event_view_for_user(query, callback_data.event_id, event)


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
        f"Ник в телеграме: @{query.from_user.username}\n"
        f"Ссылка для связи: {query.from_user.mention_html(query.from_user.full_name)}"
    )
    await query.message.edit_reply_markup(
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Заказ принят 💚", callback_data=THANK_YOU_FOR_ORDER
                    )
                ],
                # kb.back_button_row(VIEW_PRODUCTS),
            ]
        )
    )
    async for admin in database.get_db(Admin).find():
        await bot.send_message(admin["user_id"], text)


@router.callback_query(OrderEvent.filter())
async def order_product(query: types.CallbackQuery, callback_data: OrderEvent):
    await query.answer(
        "Спасибо за заказ! Свяжемся с вами в ближайшее время :)", show_alert=True
    )
    event: Event = await database.get_by_id(callback_data.event_id, Event)
    text = (
        f"Поступила заявка!\n\n"
        f"Продукт: {event.name} {utils.parse_dt_to_str(event.date)}\n"
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
                kb.back_button_row(VIEW_EVENTS),
            ]
        )
    )
    async for admin in database.get_db(Admin).find():
        await bot.send_message(admin["user_id"], text)
