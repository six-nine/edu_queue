from aiogram import Bot, types
from app.states import get_user_state, set_user_state, get_user_data, set_user_data, clear_user_data
from app.api.student import Student, StudentJoinGroupException, StudentLeaveGroupException
# from db.database_config import db
from db.db import Database
from db.database_config import PSQL_DB, PSQL_USER, PSQL_PASSWORD, PSQL_HOST, PSQL_PORT


class StudentInterface:
    def __init__(self, bot: Bot, student_tg_id: int):
        self.bot=bot
        # db = Database(dbname=PSQL_DB, user=PSQL_USER, password=PSQL_PASSWORD, host=PSQL_HOST, port=PSQL_PORT, debug=True)
        self.student = Student(student_tg_id, None)
        self.student_tg_id = student_tg_id

    async def process_invite_code(self, message: types.Message, invite_code: str):
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
            set_user_state(message.from_user.id, None)
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
        #     else:
        #         await self.bot.send_message(
        #             message.chat.id,
        #             "Не удалось добавить вас в группу. Проверьте invite-код и попробуйте снова.",
        #             reply_markup=self.back_button()
        #         )
        # except ValueError:
        #     await self.bot.send_message(
        #         message.chat.id,
        #         "Invite-код должен быть числом. Пожалуйста, попробуйте снова.",
        #         reply_markup=self.back_button()
        #     )
            '''------'''
            '''
            try:
            self.student.join_group(invite_code)
            await self.bot.send_message(
                message.chat.id,
                "Вы успешно добавлены в группу!",
                reply_markup=self.back_button()
            )
            clear_user_data(message.from_user.id)
            set_user_state(message.from_user.id, None)
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
            '''

    async def leave_group(self, message: types.Message, invite_code: str):
        try:
            self.student.leave_group(invite_code)
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
            self.student.reject_review_queue(queue_id, lab_id)
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
