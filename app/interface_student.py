from aiogram import Bot, types

from app.api.student import Student


class StudentInterface:
    def __init__(self, bot: Bot, student_name: str):
        self.bot = bot
        self.student = Student(student_name)

    async def process_invite_code(self, message: types.Message, invite_code: str):
        try:
            invite_code_int = int(invite_code)
            student_tg_id = message.from_user.id
            result = self.student.join_group(invite_code_int, student_tg_id)
            if result:
                await self.bot.send_message(message.chat.id, "Вы успешно добавлены в группу!")
            else:
                await self.bot.send_message(message.chat.id, "Не удалось добавить вас в группу. Проверьте invite-код и попробуйте снова.")
        except ValueError:
            await self.bot.send_message(message.chat.id, "Invite-код должен быть числом. Пожалуйста, попробуйте снова.")