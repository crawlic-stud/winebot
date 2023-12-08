from typing import Any
from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData

from filters.admin_filter import AdminFilter
from models import Event
import database
import utils


SAVE_EVENT = "save_event"


class CreateEvent(StatesGroup):
    name = State()
    photo = State()
    description = State()
    date = State()
    final = State()


class EditEventData(CallbackData, prefix="edit_event"):
    states_group: str
    state_name: str


EDIT_EVENT_BUTTONS = [
    [
        types.InlineKeyboardButton(
            text="✅ Сохранить",
            callback_data=SAVE_EVENT,
        )
    ],
    *utils.create_edit_keyboard(
        {
            CreateEvent.name.state: "✏️ Название",
            CreateEvent.photo.state: "✏️ Фото",
            CreateEvent.description.state: "✏️ Описание",
            CreateEvent.date.state: "✏️ Дата",
        },
        EditEventData,
    ),
]


router = Router(name="events")


async def send_final_message(m: types.Message, event: Event):
    await utils.send_event_info(
        m=m,
        event=event,
        markup=types.InlineKeyboardMarkup(inline_keyboard=EDIT_EVENT_BUTTONS),
    )


async def handle_edit(data: dict[str, Any], context: FSMContext, m: types.Message):
    is_edit = data.get("edit")
    if is_edit:
        await m.reply("Изменено!")
        await send_final_message(m, Event(**data))
        await context.set_state(CreateEvent.final)
    return is_edit


@router.message(Command("event"), AdminFilter())
async def create_order(m: types.Message, state: FSMContext):
    await m.reply("Введите название мероприятия, который хотите добавить:")
    await state.set_state(CreateEvent.name)


@router.message(CreateEvent.name)
async def add_name(m: types.Message, state: FSMContext):
    data = await state.update_data(name=m.text)
    is_edit = await handle_edit(data, state, m)
    if not is_edit:
        await m.reply("Имя добавлено! Прикрепите фотографию для афиши:")
        await state.set_state(CreateEvent.photo)


@router.message(CreateEvent.photo)
async def attach_photo(m: types.Message, state: FSMContext):
    if not m.photo:
        await m.reply("Прикрепите фотографию!")
        return
    data = await state.update_data(image_id=m.photo[-1].file_id)
    is_edit = await handle_edit(data, state, m)
    if not is_edit:
        await m.reply("Фото добавлено! Напишите описание мероприятия:")
        await state.set_state(CreateEvent.description)


@router.message(CreateEvent.description)
async def add_description(m: types.Message, state: FSMContext):
    data = await state.update_data(description=m.text)
    is_edit = await handle_edit(data, state, m)
    if not is_edit:
        await m.reply(
            "Описание добавлено! Укажите дату мероприятия в формете дд.мм.гггг:"
        )
        await state.set_state(CreateEvent.date)


@router.message(CreateEvent.date)
async def add_date(m: types.Message, state: FSMContext):
    try:
        dt = utils.parse_str_to_dt(m.text)
    except ValueError:
        await m.reply("Введите дату в формате дд.мм.гггг!")
        return

    data = await state.update_data(date=dt)
    event = Event(**data)
    await send_final_message(m, event)


@router.callback_query(EditEventData.filter())
async def edit_text_field(
    query: types.CallbackQuery, callback_data: EditEventData, state: FSMContext
):
    await query.answer("Редактируем...")
    await state.update_data(edit=True)
    m = query.message
    if callback_data.state_name == "name":
        await m.answer("Укажите новое название:")
        await state.set_state(CreateEvent.name)
    elif callback_data.state_name == "photo":
        await m.answer("Отправьте новое фото:")
        await state.set_state(CreateEvent.photo)
    elif callback_data.state_name == "description":
        await m.answer("Отправьте новое описание:")
        await state.set_state(CreateEvent.description)
    elif callback_data.state_name == "date":
        await m.answer("Отправьте новую дату в формате дд.мм.гггг:")
        await state.set_state(CreateEvent.date)


@router.callback_query(F.data == SAVE_EVENT)
async def save_order(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Сохраняем...")
    data = await state.get_data()
    event = Event(**data)
    await database.save(event)
    await state.clear()
    await query.message.delete_reply_markup()
    await query.message.answer(
        "Сохранено! Можете просмотреть или отредактировать афишу по команде /menu"
    )
