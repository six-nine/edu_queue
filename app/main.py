import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from app.interface_student import StudentInterface
from config import API_TOKEN
from app.interface_educator import EducatorInterface
from app.states import set_user_state, get_user_state, get_user_data, set_user_data, clear_user_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Пожалуйста, введите ваше имя для регистрации.")
    set_user_state(message.from_user.id, 'awaiting_name')

@router.message()
async def handle_messages(message: types.Message):
    state = get_user_state(message.from_user.id)
    if state == 'awaiting_name':
        set_user_data(message.from_user.id, 'name', message.text)
        set_user_state(message.from_user.id, 'awaiting_role')
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Студент", callback_data="role_student"),
                types.InlineKeyboardButton(text="Преподаватель", callback_data="role_educator")
            ]
        ])
        await message.answer("Вы студент или преподаватель?", reply_markup=keyboard)
    elif state == 'awaiting_invite_code':
        #await process_invite_code(message)
        student_interface = StudentInterface(bot, message.from_user.id)
        invite_code = message.text
        await student_interface.process_invite_code(message, invite_code)
    elif state and state.startswith('educator_'):
        educator_interface = EducatorInterface(bot, message.from_user.id)
        await educator_interface.handle_text_message(message)
    else:
        await message.answer("Пожалуйста, введите /start для начала.")

@router.callback_query()
async def handle_callbacks(callback_query: CallbackQuery):
    state = get_user_state(callback_query.from_user.id)
    if callback_query.data.startswith('role_'):
        role = callback_query.data.split('_')[1]
        await choose_role(callback_query, role)
    elif callback_query.data == "main_menu":
        await handle_back_to_main(callback_query, state)
    elif state and state.startswith('educator_'):
        educator_interface = EducatorInterface(bot, callback_query.from_user.id)
        await educator_interface.handle_menu_selection(callback_query)
    else:
        await callback_query.answer("Действие не распознано.", show_alert=True)

async def handle_back_to_main(callback_query: CallbackQuery, state: str):
    user_id = callback_query.from_user.id
    if state and state.startswith('educator_'):
        set_user_state(user_id, 'educator_menu')
        educator_interface = EducatorInterface(bot, user_id)
        await educator_interface.show_menu(callback_query.message)
    elif state == 'awaiting_invite_code':
        set_user_state(user_id, 'awaiting_role')
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Студент", callback_data="role_student"),
                types.InlineKeyboardButton(text="Преподаватель", callback_data="role_educator")
            ]
        ])
        await bot.send_message(callback_query.message.chat.id, "Вы студент или преподаватель?", reply_markup=keyboard)
    await callback_query.answer()

async def choose_role(callback_query: CallbackQuery, role: str):
    user_id = callback_query.from_user.id
    if role == "student":
        set_user_data(user_id, 'role', 'student')
        set_user_state(user_id, 'awaiting_invite_code')
        student_interface = StudentInterface(bot, user_id)
        await bot.send_message(
            callback_query.message.chat.id,
            "Введите invite-код для вступления в группу:",
            reply_markup=student_interface.back_button()
        )
    elif role == "educator":
        set_user_data(user_id, 'role', 'educator')
        set_user_state(user_id, 'educator_menu')
        educator_interface = EducatorInterface(bot, user_id)
        await educator_interface.show_menu(callback_query.message)
    await callback_query.answer()

async def process_invite_code(message: types.Message):
    invite_code = message.text
    role = get_user_data(message.from_user.id).get('role')
    if role == 'student':
        student_name = get_user_data(message.from_user.id).get('name')
        student_interface = StudentInterface(bot, student_name)
        await student_interface.process_invite_code(message, invite_code)

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
