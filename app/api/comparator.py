from enum import Enum
from dataclasses import dataclass
import uuid
from app.models.models import QueueStudent
from datetime import datetime, timedelta
from typing import List

@dataclass(frozen=True)
class Condition:
    class ConditionType(Enum):
        NUM_OF_ACCEPTED_LABS = 1
        IS_CURRENT_DEALINE_MISSED = 2
        NUM_OF_ATTEMPTS_BY_CURRENT_LAB = 3
        NUM_OF_MISSED_DEADLINES = 4
        DIFF_BETWEEN_CURRENT_LAB_AND_SUBMITTING = 5 # Разница между лабой, по которой дедлайн, и сдаваемой

        def get_name(self):
            if self == Condition.ConditionType.NUM_OF_ACCEPTED_LABS:
                return "Количество сданных работ"
            elif self == Condition.ConditionType.IS_CURRENT_DEALINE_MISSED:
                return "Пропущен дедлайн по текущей работе"
            elif self == Condition.ConditionType.NUM_OF_ATTEMPTS_BY_CURRENT_LAB:
                return "Количество попыток сдачи"
            elif self == Condition.ConditionType.NUM_OF_MISSED_DEADLINES:
                return "Количество пропущенных дедлайнов"
            elif self == Condition.ConditionType.DIFF_BETWEEN_CURRENT_LAB_AND_SUBMITTING:
                return "Разница между номером текущей и сдаваемой работы"
            


    class ConditionOrder(Enum):
        ASCENDING = 0
        DESCENDING = 1

    c_type: ConditionType
    c_order: ConditionOrder

    def to_int(self) -> int:
        return int(self.c_type) * 2 + int(self.c_order)

    @staticmethod
    def from_int(int_repr: int):
        return Condition(
            c_type=Condition.ConditionType(int_repr // 2),
            c_order=Condition.ConditionOrder(int_repr % 2)
        )

class Comparator:
    def __init__(self, *, 
                 id: str = None, 
                 owner_id: int | None = None, 
                 name: str, 
                 conditions: List[Condition],
                 get_student_passed_labs_count,
                 get_lab_deadline,
                 get_student_lab_attempts_count,
                 get_num_of_missed_deadlines,
                ):
        self.conditions = conditions
        # self.conditions = list(map(Condition.from_int, conditions))
        self.id = id if id is not None else str(uuid.uuid4())
        self.owner_id = owner_id
        self.name = name
        self.get_student_passed_labs_count = get_student_passed_labs_count
        self.get_lab_deadline = get_lab_deadline
        self.get_student_lab_attempts_count = get_student_lab_attempts_count
        self.get_num_of_missed_deadlines = get_num_of_missed_deadlines

    def append_condition(self, condition: Condition):
        if filter(self.conditions, lambda cond: cond.c_type == condition.c_type):
            raise ValueError(f"Condition of type {condition.c_type.name} is already presented in comparator")

        self.conditions.append(condition)

    def key(self, student: QueueStudent) -> int:
        def get_val() -> int:
            if condition.c_type == Condition.ConditionType.NUM_OF_ACCEPTED_LABS:
                return self.get_student_passed_labs_count()
            if condition.c_type == Condition.ConditionType.IS_CURRENT_DEALINE_MISSED:
                is_missed = self.get_lab_deadline(student.lab_id) < datetime.now()
                return 1 if is_missed else -1
            if condition.c_type == Condition.ConditionType.NUM_OF_ATTEMPTS_BY_CURRENT_LAB:
                return self.get_student_lab_attempts_count(student.lab_id)
            if condition.c_type == Condition.ConditionType.NUM_OF_MISSED_DEADLINES:
                return self.get_num_of_missed_deadlines(student.student_id)
            if condition.c_type == Condition.ConditionType.DIFF_BETWEEN_CURRENT_LAB_AND_SUBMITTING:
                return (self.get_lab_deadline(student.lab_id) - datetime.now()).total_seconds() / 60 / 60

        res = 0
        for condition in self.conditions:
            res *= 10000
            sign = 1 if condition.c_order == Condition.ConditionOrder.ASCENDING else -1

            res += 5000 + sign * get_val()
