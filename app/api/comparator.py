from enum import Enum
from dataclasses import dataclass
import uuid
from models.models import QueueStudent
from db.db import Database
from datetime import datetime


class Comparator:

    @dataclass(frozen=True)
    class Condition:
        class ConditionType(Enum):
            NUM_OF_ACCEPTED_LABS = 1
            IS_CURRENT_DEALINE_MISSED = 2
            NUM_OF_ATTEMPTS_BY_CURRENT_LAB = 3
            NUM_OF_MISSED_DEADLINES = 4
            DIFF_BETWEEN_CURRENT_LAB_AND_SUBMITTING = 5 # Разница между лабой, по которой дедлайн, и сдаваемой

        class ConditionOrder(Enum):
            ASCENDING = 0
            DESCENDING = 1

        c_type: ConditionType
        c_order: ConditionOrder

        def to_int(self) -> int:
            return int(self.c_type) * 2 + int(self.c_order)

        @staticmethod
        def from_int(int_repr: int) -> Comparator.Condition:
            return Comparator.Condition(
                c_type=Comparator.Condition.ConditionType(int_repr // 2),
                c_order=Comparator.Condition.ConditionOrder(int_repr % 2)
            )

    def __init__(self, *, database: Database = None, id: str = None, owner_id: int | None = None, name: str, conditions: tp.List[int]):
        self._db = database

        self.conditions = list(map(Comparator.Condition.from_int, conditions))
        self.id = id if id is not None else str(uuid.uuid4())
        self.owner_id = owner_id
        self.name = name

    def append_condition(self, condition: Comparator.Condition):
        if filter(self._conditions, lambda cond: cond.c_type == condition.c_type):
            raise ValueError(f"Condition of type {condition.c_type.name} is already presented in comparator")

        self._conditions.append(condition)

    def key(self, student: QueueStudent) -> int:
        def get_val() -> int:
            if condition.c_type == Comparator.Condition.ConditionType.NUM_OF_ACCEPTED_LABS:
                return self._db.get_student_passed_labs_count()
            if condition.c_type == Comparator.Condition.ConditionType.IS_CURRENT_DEALINE_MISSED:
                is_missed = self._db.get_lab_deadline(student.lab_id) < datetime.now()
                return 1 if is_missed else -1
            if condition.c_type == Comparator.Condition.ConditionType.NUM_OF_ATTEMPTS_BY_CURRENT_LAB:
                return self._db.get_student_lab_attempts_count(student.lab_id)
            if condition.c_type == Comparator.Condition.ConditionType.NUM_OF_MISSED_DEADLINES:
                return self._db.get_num_of_missed_deadlines(student.student_id)
            if condition.c_type == Comparator.Condition.ConditionType.DIFF_BETWEEN_CURRENT_LAB_AND_SUBMITTING:
                return self._db.get_current_lab(student.student_id)

        res = 0
        for condition in self._conditions:
            res *= 100
            sign = 1 if condition.c_order == Comparator.Condition.ConditionOrder.ASCENDING else -1

            res += 50 + sign + get_val()
