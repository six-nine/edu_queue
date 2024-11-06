from aiogram import Bot, types

class EducatorInterface:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def ask_for_invite(self, message: types.Message):
        await self.bot.send_message(message.chat.id, "Пожалуйста, пришлите мне ваш invite-код преподавателя.")

    def join_group_as_educator(self, invite_code: int):
        pass
