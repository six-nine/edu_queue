from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid
import typing as tp

class Lab:
    def __init__(self, *, id: str = None, name: str, number: int, group_id: str = None, deadline: datetime):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.number = number
        self.deadline = deadline
        self.group_id = group_id

class Group:
    def __init__(self, *, id: str = None, owner_id: int, name: str, labs: tp.List[Lab]):
        self.id = id if id is not None else str(uuid.uuid4())
        self.owner_id = owner_id
        self.name = name
        self.labs = labs

class Queue:
    def __init__(self, *, id: str = None, group_id: str, name: str, date: datetime, comparator_id: str):
        self.id = id if id is not None else str(uuid.uuid4())
        self.group_id = group_id
        self.name = name
        self.date = date
        self.comparator_id = comparator_id

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

        def get_name(self):
            if self == Condition.ConditionOrder.ASCENDING:
                return "По возрастанию"
            elif self == Condition.ConditionOrder.DESCENDING:
                return "По убыванию"

    c_type: ConditionType
    c_order: ConditionOrder

    def to_int(self) -> int:
        return int(self.c_type.value) * 2 + int(self.c_order.value)

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
                 conditions: tp.List[Condition],
                ):
        self.id = id if id is not None else str(uuid.uuid4())
        self.owner_id = owner_id
        self.name = name
        self.conditions = conditions

    def append_condition(self, condition: Condition):
        if filter(self.conditions, lambda cond: cond.c_type == condition.c_type):
            raise ValueError(f"Condition of type {condition.c_type.name} is already presented in comparator")

        self.conditions.append(condition)

class QueueStudent:
    def __init__(self, *, student_id: int, name: str, lab_id: str):
        self.student_id = student_id
        self.name = name
        self.lab_id = lab_id

class BriefUser:
    def __init__(self, *, id: int, name: str):
        self.id = id
        self.name = name

class BriefGroup:
    def __init__(self, *, id: str, name: str):
        self.id = id
        self.name = name

class BriefQueue:
    def __init__(self, *, id: str, name: str, date: datetime):
        self.id = id
        self.name = name
        self.date = date

class BriefComparator:
    def __init__(self, *, id: str, name: str):
        self.id = id
        self.name = name

