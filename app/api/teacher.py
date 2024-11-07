from datetime import datetime
import logging
from typing import Optional
from typing import List
from app.db.db import Database
from app.models.models import Queue, BriefQueue
from app.models.models import BriefGroup, Group
from app.models.models import Comparator, Lab, BriefComparator, QueueStudent
from app.api.exceptions import InvalidFutureTimeException, EduQueueException

class Teacher:
    def __init__(self, id: int, db: Database):
        self.id = id
        self.db = db
        self.current_queue = None
        self.current_student = None

    """
    Creates new empty group.
    """
    def create_group(self, group_name: str, deadlines: List[str]) -> BriefGroup:
        deadlines = [datetime.strptime(it, '%Y-%m-%d %H:%M') for it in deadlines]
        group = Group(owner_id=self.id, name=group_name, labs=[])
        labs = [Lab(name=f"Lab {i+1}", group_id=group.id, deadline=deadlines[i]) for i in range(len(deadlines))]
        group.labs = labs
        groupid = self.db.create_group(group=group)
        return next(group for group in self.db.get_teacher_groups(teacher_id=self.id) if group.id == groupid)

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
        return self.db.get_teacher_groups(teacher_id=self.id)

    """
    Adds a new `lab` to the `group`.
    """
    # def add_lab(self, group: BriefGroup, lab: Lab):
    #     TODO()

    """
    Adds a new `lab` with `name` and `deadline` to the `group`.
    """
    # def add_lab(self, group: BriefGroup, name: str, deadline: datetime):
        # if deadline <= datetime.now():
            # raise InvalidFutureTimeException(deadline)
        # TODO()

    """
    Creates and adds the queue with name `name`, date of review `date`, and `comparator_id` for labs review to the group with id `group_id`.
    """
    def add_queue(self, group_id: str, name: str, date: datetime, comparator_id: str):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M')
        if date < datetime.now():
            raise InvalidFutureTimeException(date)
        queue = Queue(group_id=group_id, name=name, date=date, comparator_id=comparator_id)
        self.db.create_queue(queue=queue)

    """
    Returns all comparators.
    """
    def get_all_comparators(self) -> List[BriefComparator]:
        return self.db.get_teacher_comparators(teacher_id=self.id) + self.db.get_system_comparators()

    """
    Cancels the class and erases queue on it.
    """
    def cancel_queue(self, queue_id: str):
        self.db.delete_queue(queue_id=queue_id)

    def is_queue_started_now(self) -> bool:
        queue = self.current_queue
        return queue != None
    
    def get_nearest_queue(self) -> BriefQueue | None:
        sorted_queues = sorted(self.db.get_teacher_queues(teacher_id=self.id), key=lambda q: q.date)
        if len(sorted_queues) == 0: return None
        return sorted_queues[0]

    """
    Replaces the `old` queue with `new` one.
    """
    def update_queue(self, old: Queue, new: Queue):
        pass

    """
    :return: list of all queues.
    """
    def get_all_queues(self) -> List[BriefQueue]:
        return self.db.get_teacher_queues(teacher_id=self.id)
    
    def get_lab_by_id(self, lab_id: str) -> str:
        return lab_id

    def start_nearest_queue_and_next_student(self) -> QueueStudent:
        queue = self.get_nearest_queue()
        self.current_queue = queue
        if queue == None: return None
        students = self.db.get_queue_students(queue_id=queue.id)
        if len(students) == 0: return None
        self.current_student = students[0]
        return students[0]

    def has_current_student(self) -> bool:
        return self.current_student != None
    
    def get_current_student(self) -> QueueStudent | None:
        return self.current_student
    
    def get_student_name(self, student_id: str) -> str:
        return student_id # TODO: return name

    """
    :return: id of the next student in the current review queue if it is not empty, or None.
    """
    def pop_next_student_from_queue(self) -> Optional[QueueStudent]:
        students = self.db.get_queue_students(queue_id=self.current_queue.id)
        if len(students) == 0:
            self.db.delete_queue(self.current_queue.id)
            self.current_queue = None
            return None
        self.current_student = students[0]
        return students[0]
    
    """
    Mark the pass result of current student in the current queue as passed lab if `passed` = `true`, 
    else mark current try as failed.
    """
    def mark_student(self, passed: bool):
        if self.current_queue == None: return
        if self.current_student == None: return
        self.db.rate_student(student_id=self.current_student.student_id, lab_id=self.current_student.lab_id, is_passed=passed)
        self.db.sign_out_queue(queue_id=self.current_queue.id, student_id=self.current_student.student_id, lab_id=self.current_student.lab_id)
        self.current_student = None

    """
    Finishes current class and clears queue if it was started.
    """
    def finish_queue(self):
        pass

    def get_group_students(self, group_id: str) -> List[int]:
        return self.db.get_group_students(group_id=group_id)

    """
    Kicks out the student with id `student_id` from the group with `group_id`.
    """
    def kick_student(self, group_id: str, student_id: int):
        print(f"groupid: {group_id}, studentid: {student_id}")
        self.db.quit_group(group_id=group_id, student_id=student_id)

    """
    Creates and stores a new comparator.
    TODO: there is "owner_id" field in Comparator. Probably it should be passed here as-is, and then owner_id should be reassigned in this method
    """
    def create_comparator(self, comparator: Comparator):
        pass
