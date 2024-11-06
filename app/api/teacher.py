from datetime import datetime
import logging
from typing import Optional
from typing import List
from app.db.db import Database
from app.models.models import Queue, Comparator, BriefGroup, Lab, Group
from app.api.exceptions import InvalidFutureTimeException, EduQueueException

class Teacher:
    def __init__(self, id: int, db: Database):
        self.id = id
        self.db = db

    """
    Creates new empty group.
    """
    def create_group(self, group_name: str) -> BriefGroup:
        groupid = Group(owner_id=self.id, name=group_name, labs=[])
        self.db.create_group(groupid)
        return next(group for group in self.db.get_teacher_groups(self.id) if group.id == groupid)

    """
    :return: invitation code of the group.
    """
    def get_group_invitation_code(self, group: BriefGroup) -> str:
        return self.get_group_invite_code(group.id)
    
    """
    :return: invitation code of the group.
    """
    def get_group_invitation_code(self, group_id: str) -> str:
        return group_id
    
    """
    :return: list of all groups.
    """
    def get_all_groups(self) -> List[BriefGroup]:
        self.db.get_teacher_groups(self.id)

    """
    Adds a new `lab` to the `group`.
    """
    def add_lab(self, group: BriefGroup, lab: Lab):
        TODO()

    """
    Adds a new `lab` with `name` and `deadline` to the `group`.
    """
    def add_lab(self, group: BriefGroup, name: str, deadline: datetime):
        if deadline <= datetime.now():
            raise InvalidFutureTimeException(deadline)
        TODO()

    """
    Creates and adds the queue with name `name`, date of review `date`, and `comparator_id` for labs review to the `group`.
    """
    def add_queue(self, group: BriefGroup, name: str, date: datetime, comparator_id: str):
        if date < datetime.now():
            raise InvalidFutureTimeException(date)
        queue = Queue(group_id=group.id, name=name, date=date, comparator_id=comparator_id)
        self.db.create_queue(queue)

    """
    Cancels the class and erases queue on it.
    """
    def cancel_queue(self, queue_id: str):
        self.db.delete_queue(queue_id=queue_id)

    """
    Replaces the `old` queue with `new` one.
    """
    def update_queue(self, old: Queue, new: Queue):
        pass

    """
    :return: list of all queues.
    """
    def get_all_queues(self) -> List[Queue]:
        pass

    """
    :return: id of the next student in the current review queue if it is not empty, or None.
    """
    def pop_review_queue() -> Optional[int]:
        pass
    
    """
    :return: id of the next student in the `queue` if it is not empty, or None.
    """
    def pop_review_queue(queue: Queue) -> Optional[int]:
        pass

    """
    Mark the `student` in the `queue` as passed lab if `passed` = `true`, 
    else mark current try as failed.
    """
    def mark_student(queue: Queue, student: int, passed: bool):
        pass

    """
    Mark the pass result of current student in the current queue.
    """
    def mark_student(passed: bool):
        pass
    
    """
    Finishes current class and clears queue if it was started.
    """
    def finish_queue():
        pass

    """
    Kicks out the student with id `student_id` from the `group`.
    """
    def kick_student(self, group: BriefGroup, student_id: int):
        pass

    """
    Creates and stores a new comparator.
    TODO: there is "owner_id" field in Comparator. Probably it should be passed here as-is, and then owner_id should be reassigned in this method
    """
    def create_comparator(self, comparator: Comparator):
        pass
