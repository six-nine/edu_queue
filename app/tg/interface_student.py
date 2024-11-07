from aiogram import Bot, types
from app.tg.states import get_user_state, set_user_state, get_user_data, set_user_data, clear_user_data
from app.api.student import Student, StudentJoinGroupException, StudentLeaveGroupException
from app.db.database_config import db


class StudentInterface:
    def __init__(self, bot: Bot, student_tg_id: int):
        self.bot=bot
        self.student = Student(student_tg_id, db)
        self.student_tg_id = student_tg_id

    async def show_menu(self, message: types.Message):
        buttons = [
            types.InlineKeyboardButton(text="Присоединиться к группе", callback_data="join_group"),
            types.InlineKeyboardButton(text="Покинуть группу", callback_data="leave_group"),
            types.InlineKeyboardButton(text="Записаться в очередь на проверку", callback_data="enroll_on_review_queue"),
            types.InlineKeyboardButton(text="Выйти из очереди на проверку", callback_data="reject_review_queue"),
            types.InlineKeyboardButton(text="Получить список текущих очередей на проверку", callback_data="get_current_review_queues"),
            types.InlineKeyboardButton(text="Получить список правил для соритровки очереди", callback_data="get_review_queue_rules"),
            types.InlineKeyboardButton(text="Вернуться в главное меню", callback_data="main_menu")
        ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+1] for i in range(0, len(buttons), 1)])
        await self.bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

    async def handle_menu_selection(self, callback_query: types.CallbackQuery):
        action = callback_query.data
        message = callback_query.message
        user_id = callback_query.from_user.id

        if action == "join_group":
            set_user_state(user_id, "student_awaiting_invite_code")
            await self.bot.send_message(
                callback_query.message.chat.id,
                "Введите invite-код для вступления в группу:",
                reply_markup=self.back_button()
            )
            await self.process_invite_code(message, message.text)
        elif action == "leave_group":
            # set_user_state(user_id, 'educator_creating_group_name')
            # await self.bot.send_message(message.chat.id, "Введите название группы:", reply_markup=self.back_button())
            set_user_state(user_id, "student_awaiting_invite_code_for_leaving_group")
            await self.bot.send_message(
                callback_query.message.chat.id,
                "Введите invite-код группы которую вы хотите покинуть:",
                reply_markup=self.back_button()
            )
            await self.leave_group(message, message.text)
        elif action == "enroll_on_review_queue":
            # set_user_state(user_id, 'educator_kick_student_group_id')
            # await self.bot.send_message(message.chat.id, "Введите ID группы:", reply_markup=self.back_button())
            await self.enroll_on_review_queue()
        elif action == "reject_review_queue":
            # set_user_state(user_id, 'educator_create_queue_group_id')
            # await self.bot.send_message(message.chat.id, "Введите ID группы для создания очереди:", reply_markup=self.back_button())
            await self.reject_review_queue()
        elif action == "get_current_review_queues":
            # set_user_state(user_id, 'educator_delete_queue_id')
            # await self.bot.send_message(message.chat.id, "Введите ID очереди, которую хотите удалить:", reply_markup=self.back_button())
            await self.get_current_review_queues(message)
        elif action == "get_review_queue_rules":
            # set_user_state(user_id, 'educator_edit_queue_id')
            # await self.bot.send_message(message.chat.id, "Введите ID очереди, которую хотите редактировать:", reply_markup=self.back_button())
            await self.get_review_queue_rules()
        elif action == "main_menu":
            set_user_state(user_id, 'student_menu')
            await self.show_menu(message)
        else:
            await self.bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню.")

        await callback_query.answer()

    async def process_invite_code(self, message: types.Message, invite_code: str):
        # invite_code = message.text
        role = get_user_data(message.from_user.id).get('role')
        if role == 'student':
            self.student_name = get_user_data(message.from_user.id).get('name')
            # student_interface = StudentInterface(bot, student_name)
            # await student_interface.process_invite_code(message, invite_code)
            try:
                student_tg_id = message.from_user.id
                self.student.join_group(invite_code)
                '''--------'''
                # if result:
                await self.bot.send_message(
                    message.chat.id,
                    "Вы успешно добавлены в группу!",
                    reply_markup=self.back_button()
                )
                clear_user_data(message.from_user.id)
                set_user_state(message.from_user.id, "student_menu")
            except StudentJoinGroupException:
                await self.bot.send_message(
                    message.chat.id,
                    "Не удалось добавить вас в группу. Проверьте invite-код и попробуйте снова.",
                    reply_markup=self.back_button()
                )
            except Exception as e:
                await self.bot.send_message(
                    message.chat.id,
                    f"Произошла ошибка: {str(e)}",
                    reply_markup=self.back_button()
                )

    async def leave_group(self, message: types.Message, invite_code: str):
        try:
            self.student.leave_group(invite_code)
            print(f"student leave invite_code: {invite_code}")
            await self.bot.send_message(
                message.chat.id,
                "Вы успешно вышли из группы!",
                reply_markup=self.back_button()
            )
        except StudentLeaveGroupException:
            await self.bot.send_message(
                message.chat.id,
                "Не удалось выйти из группы. Проверьте invite-код и попробуйте снова.",
                reply_markup=self.back_button()
            )
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Произошла ошибка: {str(e)}",
                reply_markup=self.back_button()
            )

    async def enroll_on_review_queue(self, message: types.Message, queue_id: str, lab_id: str):
        try:
            self.student.enroll_on_review_queue(queue_id, lab_id)
            await self.bot.send_message(
                message.chat.id,
                "Вы успешно записались в очередь на защиту!",
                reply_markup=self.back_button()
            )
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Не удалось записаться в очередь: {str(e)}",
                reply_markup=self.back_button()
            )

    async def reject_review_queue(self, message: types.Message, queue_id: str, lab_id: str):
        try:
            await self.student.reject_review_queue(queue_id, lab_id)
            await self.bot.send_message(
                message.chat.id,
                "Вы успешно вышли из очереди на защиту!",
                reply_markup=self.back_button()
            )
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Не удалось выйти из очереди: {str(e)}",
                reply_markup=self.back_button()
            )

    async def get_current_review_queues(self, message: types.Message):
        try:
            queues = self.student.get_current_review_queues()
            if queues:
                queues_text = '\n'.join([f"{queue.queue_id}: {queue.name}" for queue in queues])
                await self.bot.send_message(
                    message.chat.id,
                    f"Ваши текущие очереди на защиту:\n{queues_text}",
                    reply_markup=self.back_button()
                )
            else:
                await self.bot.send_message(
                    message.chat.id,
                    "У вас нет текущих очередей на защиту.",
                    reply_markup=self.back_button()
                )
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Не удалось получить список очередей: {str(e)}",
                reply_markup=self.back_button()
            )

    async def get_review_queue_rules(self, message: types.Message, queue_id: str):
        try:
            rules = self.student.get_review_queue_rules(queue_id)
            if rules:
                rules_text = '\n'.join(rules)
                await self.bot.send_message(
                    message.chat.id,
                    f"Правила сортировки очереди {queue_id}:\n{rules_text}",
                    reply_markup=self.back_button()
                )
            else:
                await self.bot.send_message(
                    message.chat.id,
                    f"Для очереди {queue_id} не найдены правила сортировки.",
                    reply_markup=self.back_button()
                )
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Не удалось получить правила сортировки: {str(e)}",
                reply_markup=self.back_button()
            )

    def back_button(self) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="main_menu")]
        ])
        return keyboard
