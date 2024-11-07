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
                message.chat.id,
                "Введите invite-код для вступления в группу:",
                reply_markup=self.back_button()
            )
            print("join_group action")
            await self.process_invite_code(message, message.text)
        elif action == "leave_group":
            set_user_state(user_id, "student_awaiting_leaving_group_invite")
            await self.bot.send_message(
                message.chat.id,
                "Введите invite-код группы которую вы хотите покинуть:",
                reply_markup=self.back_button()
            )
            print(f"leave_group message.text == 'Выберите действие:', message.text = {message.text}, {message.text == 'Выберите действие:'}")
            if message.text != "Выберите действие:":
                print("leave_group action")
                await self.leave_group(message, message.text)
        elif action == "enroll_on_review_queue":
            set_user_state(user_id, 'student_enroll_on_review_queue')
            await self.bot.send_message(
                message.chat.id,
                "Введите id очереди на проверку в которую вы хотите записаться:",
                reply_markup=self.back_button()
            )
        elif action == "reject_review_queue":
            set_user_state(user_id, 'student_reject_review_queue')
            await self.bot.send_message(
                message.chat.id,
                "Введите id очереди на проверку из которой вы хотите выйти:",
                reply_markup=self.back_button()
            )
        elif action == "get_current_review_queues":
            set_user_state(user_id, 'student_get_current_review_queues')
            await self.get_current_review_queues(message)
        elif action == "get_review_queue_rules":
            set_user_state(user_id, 'student_get_review_queue_rules')
            await self.bot.send_message(
                message.chat.id,
                "Введите id очереди для которой нужно вывести правила сортировки:",
                reply_markup=self.back_button()
            )
            if message.text != "Выберите действие:":
                print("get_review_queue_rules action")
                await self.get_review_queue_rules(message, message.text)
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
            try:
                # student_tg_id = message.from_user.id
                self.student.join_group(invite_code)
                '''--------'''
                # if result:
                await self.bot.send_message(
                    message.chat.id,
                    "Вы успешно добавлены в группу!",
                    reply_markup=self.back_button()
                )
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
            self.student_name = get_user_data(message.from_user.id).get('name')
            self.student.leave_group(invite_code)
            print(f"student leave invite_code: {invite_code}")
            await self.bot.send_message(
                message.chat.id,
                f"Вы успешно вышли из группы '{invite_code}'! Можете ввести еще одну группу которую вы хотите покинуть или вернутся в меню.",
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
    
    async def handle_text_message(self, message: types.Message):
        state = get_user_state(message.from_user.id)
        if state == 'student_enroll_on_review_queue':
            await self.enroll_on_review_queue_step2(message)
        elif state == 'student_enroll_on_review_queue_enter_queue_id':
            await self.enroll_on_review_queue_step3(message)
        elif state == 'student_reject_review_queue':
            await self.reject_review_queue_step2(message)
        elif state == 'student_reject_review_queue_enter_queue_id':
            await self.reject_review_queue_step3(message)
        else:
            await self.bot.send_message(message.chat.id, "Пожалуйста, используйте команды из меню.", reply_markup=self.back_button())

    async def enroll_on_review_queue(self, message: types.Message, queue_id: str, lab_id: str):
        try:
            self.student.enroll_on_review_queue(queue_id, lab_id)
            await self.bot.send_message(
                message.chat.id,
                f"Вы успешно записались в очередь '{queue_id}' на защиту лабы '{lab_id}'!",
                reply_markup=self.back_button()
            )
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Не удалось записаться в очередь: {str(e)}",
                reply_markup=self.back_button()
            )

    async def enroll_on_review_queue_step2(self, message: types.Message):
        enroll_review_queue_id = message.text
        set_user_data(message.from_user.id, 'enroll_review_queue_id', enroll_review_queue_id)
        set_user_state(message.from_user.id, 'student_enroll_on_review_queue_enter_queue_id')
        # TODO queue_id validation
        await self.bot.send_message(message.chat.id, "Введите номер лабы которую вы хотите защитить:", reply_markup=self.back_button())
    
    async def enroll_on_review_queue_step3(self, message: types.Message):
        enroll_review_lab_id = message.text
        # set_user_data(message.from_user.id, 'enroll_review_lab_id', enroll_review_lab_id)
        set_user_state(message.from_user.id, 'student_enroll_on_review_queue_enter_lab_id')
        # TODO lab_id validation
        queue_id = get_user_data(message.from_user.id).get('enroll_review_queue_id')
        lab_id = enroll_review_lab_id
        await self.enroll_on_review_queue(message, queue_id, lab_id)

    async def reject_review_queue(self, message: types.Message, queue_id: str, lab_id: str):
        try:
            self.student.reject_review_queue(queue_id, lab_id)
            await self.bot.send_message(
                message.chat.id,
                f"Вы успешно вышли из очереди '{queue_id}' на защиту лабы '{lab_id}'!",
                reply_markup=self.back_button()
            )
            print(f"delete from queue_subscribers where  queue_id = {queue_id} student_id = {self.student_tg_id} lab_id = {lab_id}")
        except Exception as e:
            await self.bot.send_message(
                message.chat.id,
                f"Не удалось выйти из очереди: {str(e)}",
                reply_markup=self.back_button()
            )

    async def reject_review_queue_step2(self, message: types.Message):
        reject_review_queue_id = message.text
        set_user_data(message.from_user.id, 'reject_review_queue_id', reject_review_queue_id)
        set_user_state(message.from_user.id, 'student_reject_review_queue_enter_queue_id')
        # TODO queue_id validation
        await self.bot.send_message(message.chat.id, "Введите номер лабы по которой вы хотите отменить проверку:", reply_markup=self.back_button())
    
    async def reject_review_queue_step3(self, message: types.Message):
        reject_review_lab_id = message.text
        # set_user_data(message.from_user.id, 'enroll_review_lab_id', enroll_review_lab_id)
        set_user_state(message.from_user.id, 'student_reject_review_queue_enter_lab_id')
        # TODO lab_id validation
        queue_id = get_user_data(message.from_user.id).get('reject_review_queue_id')
        lab_id = reject_review_lab_id
        await self.reject_review_queue(message, queue_id, lab_id)

    async def get_current_review_queues(self, message: types.Message):
        try:
            queues = self.student.get_current_review_queues()
            if queues:
                queues_text = '\n'.join([f"{queue.id}: {queue.name}" for queue in queues])
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
