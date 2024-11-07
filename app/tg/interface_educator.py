from aiogram import Bot, types
from app.tg.states import get_user_state, set_user_state, get_user_data, set_user_data

class EducatorInterface:
    def __init__(self, bot: Bot, teacher_tg_id: int):
        self.bot = bot
        self.teacher_tg_id = teacher_tg_id

    async def show_menu(self, message: types.Message):
        buttons = [
            types.InlineKeyboardButton(text="Создать группу", callback_data="create_group"),
            types.InlineKeyboardButton(text="Исключить студента", callback_data="kick_student"),
            types.InlineKeyboardButton(text="Создать очередь защиты", callback_data="create_queue"),
            types.InlineKeyboardButton(text="Удалить очередь", callback_data="delete_queue"),
            types.InlineKeyboardButton(text="Редактировать очередь", callback_data="edit_queue"),
            types.InlineKeyboardButton(text="Следующий студент", callback_data="next_student"),
            types.InlineKeyboardButton(text="Добавить правило сортировки", callback_data="add_sorting_rule"),
            types.InlineKeyboardButton(text="Вернуться в главное меню", callback_data="main_menu")
        ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+1] for i in range(0, len(buttons), 1)])
        await self.bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

    async def handle_menu_selection(self, callback_query: types.CallbackQuery):
        action = callback_query.data
        message = callback_query.message
        user_id = callback_query.from_user.id

        if action == "create_group":
            set_user_state(user_id, 'educator_creating_group_name')
            await self.bot.send_message(message.chat.id, "Введите название группы:", reply_markup=self.back_button())
        elif action == "kick_student":
            set_user_state(user_id, 'educator_kick_student_group_id')
            await self.bot.send_message(message.chat.id, "Введите ID группы:", reply_markup=self.back_button())
        elif action == "create_queue":
            set_user_state(user_id, 'educator_create_queue_group_id')
            await self.bot.send_message(message.chat.id, "Введите ID группы для создания очереди:", reply_markup=self.back_button())
        elif action == "delete_queue":
            set_user_state(user_id, 'educator_delete_queue_id')
            await self.bot.send_message(message.chat.id, "Введите ID очереди, которую хотите удалить:", reply_markup=self.back_button())
        elif action == "edit_queue":
            set_user_state(user_id, 'educator_edit_queue_id')
            await self.bot.send_message(message.chat.id, "Введите ID очереди, которую хотите редактировать:", reply_markup=self.back_button())
        elif action == "next_student":
            set_user_state(user_id, 'educator_next_student_queue_id')
            await self.bot.send_message(message.chat.id, "Введите ID очереди:", reply_markup=self.back_button())
        elif action == "add_sorting_rule":
            set_user_state(user_id, 'educator_add_sorting_rule_queue_id')
            await self.bot.send_message(message.chat.id, "Введите ID очереди для добавления правила сортировки:", reply_markup=self.back_button())
        elif action == "main_menu":
            set_user_state(user_id, 'educator_menu')
            await self.show_menu(message)
        else:
            await self.bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню.")

        await callback_query.answer()

    async def handle_text_message(self, message: types.Message):
        state = get_user_state(message.from_user.id)
        if state == 'educator_creating_group_name':
            await self.create_group_step2(message)
        elif state == 'educator_creating_group_lab_count':
            await self.create_group_step3(message)
        elif state == 'educator_creating_group_lab_deadlines':
            await self.create_group_step4(message)
        else:
            await self.bot.send_message(message.chat.id, "Пожалуйста, используйте команды из меню.", reply_markup=self.back_button())

    async def create_group_step2(self, message: types.Message):
        group_name = message.text
        set_user_data(message.from_user.id, 'group_name', group_name)
        set_user_state(message.from_user.id, 'educator_creating_group_lab_count')
        await self.bot.send_message(message.chat.id, "Введите количество лабораторных работ в группе:", reply_markup=self.back_button())

    async def create_group_step3(self, message: types.Message):
        try:
            lab_count = int(message.text)
            set_user_data(message.from_user.id, 'lab_count', lab_count)
            set_user_state(message.from_user.id, 'educator_creating_group_lab_deadlines')
            await self.bot.send_message(message.chat.id, "Введите дедлайны для лабораторных работ через запятую в формате 'YYYY-MM-DD HH:MM':", reply_markup=self.back_button())
        except ValueError:
            await self.bot.send_message(message.chat.id, "Пожалуйста, введите число.", reply_markup=self.back_button())

    async def create_group_step4(self, message: types.Message):
        deadlines = message.text.split(',')
        lab_count = get_user_data(message.from_user.id).get('lab_count')
        if len(deadlines) != lab_count:
            await self.bot.send_message(message.chat.id, f"Количество дедлайнов не соответствует количеству лабораторных работ ({lab_count}). Попробуйте снова.", reply_markup=self.back_button())
            return


        set_user_state(message.from_user.id, 'educator_menu')
        await self.show_menu(message)

    def back_button(self) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="main_menu")]
        ])
        return keyboard
