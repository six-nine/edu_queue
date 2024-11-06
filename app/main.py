import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from config import API_TOKEN
from app.interface_student import StudentInterface
from app.interface_educator import EducatorInterface

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

user_states = {}
user_data = {}

def get_user_state(user_id):
    return user_states.get(user_id)

def set_user_state(user_id, state):
    user_states[user_id] = state

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Пожалуйста, введите ваше имя для регистрации.")
    set_user_state(message.from_user.id, 'awaiting_name')

@router.message()
async def handle_messages(message: types.Message):
    state = get_user_state(message.from_user.id)
    if state == 'awaiting_name':
        await process_name(message)
    elif state == 'awaiting_role':
        await choose_role(message)
    elif state == 'awaiting_invite_code':
        await process_invite_code(message)
    else:
        await message.answer("Пожалуйста, введите /start для начала.")

async def process_name(message: types.Message):
    user_name = message.text
    user_data[message.from_user.id] = {'name': user_name}
    set_user_state(message.from_user.id, 'awaiting_role')
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Студент"),
                types.KeyboardButton(text="Преподаватель")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Вы студент или преподаватель?", reply_markup=keyboard)

async def choose_role(message: types.Message):
    if message.text == "Студент":
        user_data[message.from_user.id]['role'] = 'student'
        set_user_state(message.from_user.id, 'awaiting_invite_code')
        await message.answer("Введите invite-код для вступления в группу.")
    elif message.text == "Преподаватель":
        user_data[message.from_user.id]['role'] = 'educator'
        set_user_state(message.from_user.id, 'awaiting_invite_code')
        await message.answer("Введите код для преподавателей.")
    else:
        await message.answer("Пожалуйста, выберите корректную роль из предложенных кнопок.")

async def process_invite_code(message: types.Message):
    invite_code = message.text
    role = user_data[message.from_user.id]['role']
    user_name = user_data[message.from_user.id]['name']
    user_tg_id = message.from_user.id

    if role == 'student':
        student_interface = StudentInterface(bot, user_name)
        await student_interface.process_invite_code(message, invite_code)
    elif role == 'educator':
        educator_interface = EducatorInterface(bot)
        await educator_interface.process_invite_code(message, invite_code)
    else:
        await message.answer("Неизвестная роль. Пожалуйста, начните сначала с команды /start.")

    set_user_state(message.from_user.id, None)
    user_data.pop(message.from_user.id, None)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
