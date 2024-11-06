import typing as tp
from models.models import BriefQueue
from db.db import Database

class StudentJoinGroupException(Exception):
    def __init__(self, student_tg_id: int, invite_code: str) -> None:
        self.student_tg_id = student_tg_id
        self.invite_code = invite_code
 
    def __str__(self) -> str:
        return f"Failed attempt to join student with student_tg_id = {self.student_tg_id} in group with invite_code (group_id) = {self.invite_code}"


class StudentLeaveGroupException(Exception):
    def __init__(self, student_tg_id: int, invite_code: str) -> None:
        self.student_tg_id = student_tg_id
        self.invite_code = invite_code
 
    def __str__(self) -> str:
        return f"Failed attempt to remove student with student_tg_id = {self.student_tg_id} from group with invite_code (group_id) = {self.invite_code}"


class Student:

    def __init__(self, student_tg_id: int, database: Database) -> None:
        self.student_tg_id = student_tg_id
        self.database = database
        self.is_subscribed_review_queue_enroll_start_notifications = True


    def join_group(self, invite_code: str) -> None:
        bool_result = self.database.join_group(invite_code, self.student_tg_id)
        if not bool_result:
            raise StudentJoinGroupException(self.student_tg_id, invite_code)


    def leave_group(self, invite_code: str) -> None:
        bool_result = self.database.quit_group(invite_code, self.student_tg_id)
        if not bool_result:
            raise StudentLeaveGroupException(self.student_tg_id, invite_code)


    # def subscribe_review_queue_enroll_start_notifications(self):
    #     self.is_subscribed_review_queue_enroll_start_notifications = True
    #     # INSERT INTO "notification subscribers table"


    # def unsubscribe_review_queue_enroll_start_notifications(self):
    #     self.is_subscribed_review_queue_enroll_start_notifications = False
    #     # DELETE FROM "notification subscribers table"


    def enroll_on_review_queue(self, queue_id: str, lab_id: str) -> None:
        self.database.sign_in_queue(queue_id, self.student_tg_id, lab_id)


    def reject_review_queue(self, queue_id: str, lab_id: str) -> None:
        self.database.sign_out_queue(queue_id, self.student_tg_id, lab_id)


    def get_current_review_queues(self) -> tp.List[BriefQueue]:
        return self.database.get_student_queues(self.student_tg_id)


    def get_review_queue_rules(self, queue_id: str) -> tp.List[str]:
        queue_obj = self.database.get_queue(queue_id)
        return [t.name for t in self.database.get_comparator(queue_obj.comparator_id).data]