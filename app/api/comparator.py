from enum import Enum
from dataclasses import dataclass

class Comparator:

    @dataclass(frozen=True)
    class Condition:
        class ConditionType(Enum):
            NUM_OF_ACCEPTED_LABS = 1
            IS_CURRENT_DEALINE_MISSED = 2
            NUM_OF_ATTEMPTS_BY_CURRENT_LAB = 3
            NUM_OF_MISSED_DEADLINES = 4


        class ConditionOrder(Enum):
            ASCENDING = 1
            DESCENDING = 2

        c_type: ConditionType
        c_order: ConditionOrder


    def __init__(self):
        self._conditions: list[Comparator.Condition] = list()

    def append_condition(self, condition: Comparator.Condition):
        if filter(self._conditions, lambda cond: cond.c_type == condition.c_type):
            raise ValueError(f"Condition of type {condition.c_type.name} is already presented in comparator")

        self._conditions.append(condition)

    def key(self, student: QueueStu):
        
