from aiogram import Bot, types
from app.tg.states import get_user_state, set_user_state, get_user_data, set_user_data, clear_user_data
from app.api.teacher import Teacher
from app.db.database_config import db
from app.api.comparator import Condition
from typing import List

class EducatorInterface:
    def __init__(self, bot: Bot, teacher_tg_id: int):
        self.bot = bot
        self.teacher_tg_id = teacher_tg_id
        self.teacher = Teacher(teacher_tg_id, db)

    async def show_yes_no_create_queue(self, message: types.Message, question: str):
        buttons = [
            types.InlineKeyboardButton(text="Да", callback_data="create_queue_yes"),
            types.InlineKeyboardButton(text="Нет", callback_data="create_queue_no"),
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
        await self.bot.send_message(message.chat.id, question, reply_markup=keyboard)

    async def show_rate_student_dialog(self, message: types.Message, student_name: str, lab: str):
        buttons = [
            types.InlineKeyboardButton(text="Зачет", callback_data="mark_student_passed"),
            types.InlineKeyboardButton(text="Пересдача", callback_data="mark_student_failed"),
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
        await self.bot.send_message(message.chat.id, f"Студент {student_name} с работой {lab}", reply_markup=keyboard)

    async def show_menu(self, message: types.Message):
        has_current_student = self.teacher.has_current_student()
        next_student_button = types.InlineKeyboardButton(text="Следующий студент", callback_data="next_student")
        mark_student_button = types.InlineKeyboardButton(text="Оценить студента", callback_data="mark_student")
        student_button = next_student_button if not has_current_student else mark_student_button
        buttons = [
            types.InlineKeyboardButton(text="Создать группу", callback_data="create_group"),
            types.InlineKeyboardButton(text="Исключить студента", callback_data="kick_student"),
            types.InlineKeyboardButton(text="Создать очередь защиты", callback_data="create_queue"),
            types.InlineKeyboardButton(text="Удалить очередь", callback_data="delete_queue"),
            # types.InlineKeyboardButton(text="Редактировать очередь", callback_data="edit_queue"),
            student_button,
            types.InlineKeyboardButton(text="Добавить правило приоритетов", callback_data="add_sorting_rule"),
            types.InlineKeyboardButton(text="Вернуться в главное меню", callback_data="main_menu")
        ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+1] for i in range(0, len(buttons), 1)])
        await self.bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

    async def show_comparators_choice(self, message: types.Message, comptypes: List[Condition.ConditionType]):
        # TODO: add choice finish button
        buttons = [types.InlineKeyboardButton(text=t.get_name(), callback_data=f"comparator_{t}") for t in comptypes]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+1] for i in range(0, len(buttons), 1)])
        await self.bot.send_message(message.chat.id, f"Выберите наиболее приоритетное свойство", reply_markup=keyboard)


    async def handle_menu_selection(self, callback_query: types.CallbackQuery):
        action = callback_query.data
        message = callback_query.message
        user_id = callback_query.from_user.id

        if action == "create_group":
            set_user_state(user_id, 'educator_creating_group_name')
            await self.bot.send_message(message.chat.id, "Введите название группы:", reply_markup=self.back_button())
        elif action == "kick_student":
            set_user_state(user_id, 'educator_kick_student_enter_group')
            groups_lines = self.get_groups_list_str()
            await self.bot.send_message(message.chat.id, f"Введите номер группы, из которой вы хотите удалить студента:\n{groups_lines}", reply_markup=self.back_button())
        elif action == "create_queue":
            set_user_state(user_id, 'educator_create_queue_group_id')
            groups_lines = self.get_groups_list_str()
            await self.bot.send_message(message.chat.id, f"Введите номер группы для создания очереди:\n{groups_lines}", reply_markup=self.back_button())
        elif action == "delete_queue":
            set_user_state(user_id, 'educator_delete_queue_id')
            queues_lines = self.get_queues_list_str()
            await self.bot.send_message(message.chat.id, f"Введите номер очереди, которую хотите удалить:\n{queues_lines}", reply_markup=self.back_button())
        elif action == "edit_queue":
            set_user_state(user_id, 'educator_edit_queue_id')
            await self.bot.send_message(message.chat.id, "Введите ID очереди, которую хотите редактировать:", reply_markup=self.back_button())
        elif action == "next_student":
            set_user_state(user_id, 'educator_next_student_queue_id')
            await self.next_student_in_queue_step_1(message)
        # elif action == "add_sorting_rule":
            # set_user_state(user_id, 'educator_add_sorting_rule_queue_id')
            # await self.bot.send_message(message.chat.id, "Введите ID очереди для добавления правила сортировки:", reply_markup=self.back_button())
        elif action == "main_menu":
            set_user_state(user_id, 'educator_menu')
            await self.show_menu(message)
        elif action == 'create_queue_yes':
            student = self.teacher.start_nearest_queue_and_next_student()
            if student == None:
                await self.bot.send_message(message.chat.id, "В очереди нет студентов")
            else:
                lab = self.teacher.get_lab_by_id(student.lab_id)
                await self.bot.send_message(message.chat.id, f"Следующий студент: {student.student_id} с работой {lab}")

            clear_user_data(user_id)
            set_user_state(user_id, 'educator_menu')
            await self.show_menu(message)
        elif action == 'create_queue_no':
            clear_user_data(user_id)
            set_user_state(user_id, 'educator_menu')
            await self.show_menu(message)
        elif action == 'mark_student':
            student = self.teacher.get_current_student()
            if student == None:
                await self.bot.send_message(message.chat.id, f"Некого оценивать")
                clear_user_data(user_id)
                set_user_state(user_id, 'educator_menu')
                await self.show_menu(message)
            else:
                set_user_state(user_id, 'educator_mark_student')
                await self.show_rate_student_dialog(message, self.teacher.get_student_name(student.student_id), self.teacher.get_lab_by_id(student.lab_id))
        elif action == 'mark_student_passed':
            self.teacher.mark_student(True)
            await self.bot.send_message(message.chat.id, f"Ответ принят")
            clear_user_data(user_id)
            set_user_state(user_id, 'educator_menu')
            await self.show_menu(message)
        elif action == 'mark_student_failed':
            self.teacher.mark_student(False)
            await self.bot.send_message(message.chat.id, f"Ответ принят")
            clear_user_data(user_id)
            set_user_state(user_id, 'educator_menu')
            await self.show_menu(message)
        elif action == 'add_sorting_rule':
            set_user_state(user_id, 'educator_add_sorting_rule_name')
            await self.bot.send_message(message.chat.id, f"Введите название нового правила:")

            
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
        elif state == 'educator_kick_student_enter_group':
            await self.kick_student_step1(message)
        elif state == 'educator_kick_student_enter_student':
            await self.kick_student_step2(message)
        elif state == 'educator_create_queue_group_id':
            await self.create_queue_step_1(message)
        elif state == 'educator_create_queue_name':
            await self.create_queue_step_2(message)
        elif state == 'educator_create_queue_date':
            await self.create_queue_step_3(message)
        elif state == 'educator_create_queue_comparator':
            await self.create_queue_step_4(message)
        elif state == 'educator_delete_queue_id':
            await self.delete_queue_step_1(message)
        elif state == 'educator_next_student_queue_id':
            await self.next_student_in_queue_step_1(message)
        elif state == 'educator_add_sorting_rule_name':
            await self.add_sorting_rule_step_1(message)
        elif state == 'educator_add_sorting_rule_add_type':
            print("hi") # TODO

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
        group_name = get_user_data(message.from_user.id).get('group_name')
        groupid = self.teacher.create_group(group_name, deadlines).id
        await self.bot.send_message(message.chat.id, f"Код с приглашением в группу: {groupid}")

        set_user_state(message.from_user.id, 'educator_menu')
        await self.show_menu(message)

    async def kick_student_step1(self, message: types.Message):
        set_user_state(message.from_user.id, 'educator_kick_student_enter_student')
        groupid = self.group_id_from_num(int(message.text))
        set_user_data(message.from_user.id, 'groupid', groupid)
        students_lines = self.get_students_list_str(groupid)
        await self.bot.send_message(message.chat.id, f"Введите номер студента, которого вы хотите удалить из группы:\n{students_lines}", reply_markup=self.back_button())
    
    async def kick_student_step2(self, message: types.Message):
        groupid = get_user_data(message.from_user.id).get('groupid')
        studentid = self.student_id_from_num(groupid, int(message.text))
        self.teacher.kick_student(group_id=groupid, student_id=studentid)
        await self.bot.send_message(message.chat.id, "Студент успешно удален", reply_markup=self.back_button())
    
        clear_user_data(message.from_user.id)
        set_user_state(message.from_user.id, 'educator_menu')
        await self.show_menu(message)

    async def create_queue_step_1(self, message: types.Message):
        set_user_state(message.from_user.id, "educator_create_queue_name")
        groupid = self.group_id_from_num(int(message.text))
        set_user_data(message.from_user.id, 'groupid', groupid)
        await self.bot.send_message(message.chat.id, "Введите название сдачи:", reply_markup=self.back_button())

    async def create_queue_step_2(self, message: types.Message):
        set_user_state(message.from_user.id, "educator_create_queue_date")
        queue_name = message.text
        set_user_data(message.from_user.id, 'queue_name', queue_name)
        await self.bot.send_message(message.chat.id, "Введите дату и время сдачи в формате в формате 'YYYY-MM-DD HH:MM':", reply_markup=self.back_button())

    async def create_queue_step_3(self, message: types.Message):
        set_user_state(message.from_user.id, "educator_create_queue_comparator")
        date = message.text
        set_user_data(message.from_user.id, 'queue_date', date)
        comparators_lines = self.get_comparators_list_str()
        await self.bot.send_message(message.chat.id, f"Введите номер компаратора для очереди:\n{comparators_lines}", reply_markup=self.back_button())

    async def create_queue_step_4(self, message: types.Message):
        comparatorid = self.comparator_id_from_num(int(message.text))
        date = get_user_data(message.from_user.id).get('queue_date')
        queue_name = get_user_data(message.from_user.id).get('queue_name')
        groupid = get_user_data(message.from_user.id).get('groupid')
        
        self.teacher.add_queue(groupid, queue_name, date, comparatorid)
        await self.bot.send_message(message.chat.id, f"Очередь создана", reply_markup=self.back_button())

        clear_user_data(message.from_user.id)
        set_user_state(message.from_user.id, 'educator_menu')
        await self.show_menu(message)

    async def delete_queue_step_1(self, message: types.Message):
        queueid = self.group_id_from_num(int(message.text))
        self.teacher.cancel_queue(queue_id=queueid)

        await self.bot.send_message(message.chat.id, f"Очередь удалена", reply_markup=self.back_button())
        clear_user_data(message.from_user.id)
        set_user_state(message.from_user.id, 'educator_menu')
        await self.show_menu(message)

    async def next_student_in_queue_step_1(self, message: types.Message):
        if self.teacher.is_queue_started_now():
            student = self.teacher.pop_next_student_from_queue()
            if student == None:
                await self.bot.send_message(message.chat.id, "В очереди больше нет студентов", reply_markup=self.back_button())
                clear_user_data(message.from_user.id)
                set_user_state(message.from_user.id, 'educator_menu')
                await self.show_menu(message)
            else:
                lab = self.teacher.get_lab_by_id(student)
                await self.bot.send_message(message.chat.id, f"Следующий студент: {student.student_id} с работой {lab}")
                clear_user_data(message.from_user.id)
                set_user_state(message.from_user.id, 'educator_menu')
                await self.show_menu(message)

        else:
            nearest_queue = self.teacher.get_nearest_queue()
            if nearest_queue == None:
                await self.bot.send_message(message.chat.id, "Нет ближайших очередей, отдыхайте =)", reply_markup=self.back_button())
                clear_user_data(message.from_user.id)
                set_user_state(message.from_user.id, 'educator_menu')
                await self.show_menu(message)
            else:
                await self.show_yes_no_create_queue(message, f"Сдача еще не началась, начать сдачу очереди '{nearest_queue.name} - {nearest_queue.date}?")

    async def add_sorting_rule_step_1(self, message: types.Message):
        set_user_state(message.from_user.id, "educator_add_sorting_rule_add_type")
        sorting_name = message.text
        set_user_data(message.from_user.id, 'sorting_rule_name', sorting_name)
        comparators = get_user_data(message.from_user.id).get('comparators')
        comparators = comparators if comparators != None else [t for t in Condition.ConditionType]
        await self.show_comparators_choice(message, comparators)


    def back_button(self) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="main_menu")]
        ])
        return keyboard
    
    def get_groups_list_str(self) -> str:
        groups = self.teacher.get_all_groups()
        groups_lines = "\n".join([f"{i+1}. {groups[i].name}" for i in range(len(groups))])
        return groups_lines
    
    def group_id_from_num(self, num: int) -> str:
        return self.teacher.get_all_groups()[num - 1].id
    
    def get_students_list_str(self, group_id: str) -> str:
        students = self.teacher.get_group_students(group_id)
        students_lines = "\n".join([f"{i+1}. {str(students[i])}" for i in range(len(students))])
        return students_lines
    
    def student_id_from_num(self, group_id: str, num: int) -> str:
        return self.teacher.get_group_students(group_id)[num - 1]
    
    def get_comparators_list_str(self) -> str:
        comparators = self.teacher.get_all_comparators()
        comparators_lines = "\n".join([f"{i+1}. {str(comparators[i].name)}" for i in range(len(comparators))])
        return comparators_lines
    
    def comparator_id_from_num(self, num: int) -> str:
        return self.teacher.get_all_comparators()[num - 1].id
    
    def get_queues_list_str(self) -> str:
        queues = self.teacher.get_all_queues()
        queues_lines = "\n".join([f"{i+1}. {queues[i].name} - {str(queues[i].date)}" for i in range(len(queues))])
        return queues_lines
    
    def queue_id_from_num(self, num: int) -> str:
        return self.teacher.get_all_queues()[num - 1].id
