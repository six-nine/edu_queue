from datetime import datetime
from enum import Enum
import uuid
import typing as tp


class Lab:
    def __init__(self, *, id: str = None, number: int, group_id: str = None, deadline: datetime):
        self.id = id if id is not None else str(uuid.uuid4())
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

class QueueStudent:
    def __init__(self, *, student_id: int, lab_id: str):
        self.student_id = student_id
        self.lab_id = lab_id

class ComparatorType(Enum):
    TYPE0 = 0,
    TYPE1 = 1,
    TYPE2 = 2,

class Comparator:
    def __init__(self, *, id: str = None, owner_id: int | None = None, name: str, data: tp.List[ComparatorType]):
        self.id = id if id is not None else str(uuid.uuid4())
        self.owner_id = owner_id
        self.name = name
        self.data = data

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

