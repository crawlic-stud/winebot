from aiogram import types, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

import database
from handlers.events import EDIT_EVENT_BUTTONS
from handlers.product import EDIT_PRODUCT_BUTTONS
import utils
import kb
from models import Event, Product
from filters.admin_filter import AdminFilter


VIEW_PRODUCTS = "admin_view_products"
ORDER_PRODUCT = "admin_order_product"
VIEW_EVENTS = "admin_view_events"
GO_TO_MENU = "admin_go_to_menu"


class AdminView(StatesGroup):
    products = State()
    product_detail = State()

    events = State()
    event_detail = State()


class ViewProduct(CallbackData, prefix="admin_view_product"):
    product_id: str


class ViewEvent(CallbackData, prefix="admin_view_event"):
    event_id: str


router = Router(name="admin_panel")


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
@router.message(Command("admin"), AdminFilter())
async def send_menu(update: types.Message | types.CallbackQuery):
    text = "Что редактируем?"
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


@router.callback_query(F.data == VIEW_EVENTS)
async def view_events(query: types.CallbackQuery):
    await query.answer("Показываем...")
    text = "Список доступных мероприятий:"
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=await get_all_events_kb())
    m = query.message
    if m.photo:
        await m.delete()
        await m.answer(text=text, reply_markup=reply_markup)
    else:
        await m.edit_text(text=text, reply_markup=reply_markup)


async def render_product_view_for_admin(
    query: types.CallbackQuery, object_id: str, product: Product
):
    await utils.send_product_info(
        m=query.message,
        product=product,
        markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                *EDIT_PRODUCT_BUTTONS,
                kb.delete_obj_row(object_id, Product.get_collection()),
                kb.back_button_row(VIEW_PRODUCTS),
            ]
        ),
        edit=True,
    )


async def render_event_view_for_admin(
    query: types.CallbackQuery, object_id: str, event: Event
):
    await utils.send_event_info(
        m=query.message,
        event=event,
        markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                *EDIT_EVENT_BUTTONS,
                kb.delete_obj_row(object_id, Event.get_collection()),
                kb.back_button_row(VIEW_EVENTS),
            ]
        ),
        edit=True,
    )


@router.callback_query(ViewProduct.filter())
async def view_product(
    query: types.CallbackQuery, callback_data: ViewProduct, state: FSMContext
):
    await query.answer("Показываем")
    product: Product = await database.get_by_id(callback_data.product_id, Product)
    await state.update_data(
        {**product.model_dump(), "object_id": callback_data.product_id}
    )
    await render_product_view_for_admin(query, callback_data.product_id, product)


@router.callback_query(ViewEvent.filter())
async def view_event(
    query: types.CallbackQuery, callback_data: ViewEvent, state: FSMContext
):
    await query.answer("Показываем")
    event: Event = await database.get_by_id(callback_data.event_id, Event)
    await state.update_data({**event.model_dump(), "object_id": callback_data.event_id})
    await render_event_view_for_admin(query, callback_data.event_id, event)
