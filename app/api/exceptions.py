from datetime import datetime


"""
Base exception class produced in API.
"""
class EduQueueException(Exception):
    pass

class InvalidFutureTimeException(EduQueueException):
    def __init__(self, deadline: datetime):
        self.deadlne = deadline

    def __str__(self) -> str:
        return f"Deadline must be time in the future, but got {self.deadline}"
