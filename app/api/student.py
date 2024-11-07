import typing as tp
from app.models.models import BriefQueue, Lab
from app.db.db import Database
from app.db.database_config import db


class StudentJoinGroupException(Exception):
    def __init__(self, student_tg_id: int, invite_code: str) -> None:
        self.student_tg_id = student_tg_id
        self.invite_code = invite_code
 
    def __str__(self) -> str:
        return f"Не удалось добавить в группу с invite_code (group_id) = {self.invite_code}!"


class StudentLeaveGroupException(Exception):
    def __init__(self, student_tg_id: int, invite_code: str) -> None:
        self.student_tg_id = student_tg_id
        self.invite_code = invite_code
 
    def __str__(self) -> str:
        return f"Не удалось из группы с invite_code (group_id) = {self.invite_code}!"


class StudentLabNotFoundException(Exception):
    def __init__(self, lab_id: str) -> None:
        self.lab_id = lab_id
 
    def __str__(self) -> str:
        return f"Лаба с lab_id = {self.lab_id} не найдена!"

class Student:

    def __init__(self, student_tg_id: int, database: Database) -> None:
        self.student_tg_id = student_tg_id
        self.database = database
        self.is_subscribed_review_queue_enroll_start_notifications = True


    def join_group(self, invite_code: str) -> None:
        bool_result = self.database.join_group(group_id=invite_code, student_id=self.student_tg_id)
        if not bool_result:
            raise StudentJoinGroupException(self.student_tg_id, invite_code)


    def leave_group(self, invite_code: str) -> None:
        bool_result = self.database.quit_group(group_id=invite_code, student_id=self.student_tg_id)
        if not bool_result:
            raise StudentLeaveGroupException(self.student_tg_id, invite_code)


    # def subscribe_review_queue_enroll_start_notifications(self):
    #     self.is_subscribed_review_queue_enroll_start_notifications = True
    #     # INSERT INTO "notification subscribers table"


    # def unsubscribe_review_queue_enroll_start_notifications(self):
    #     self.is_subscribed_review_queue_enroll_start_notifications = False
    #     # DELETE FROM "notification subscribers table"


    def enroll_on_review_queue(self, queue_id: str, lab_id: str) -> Lab:
        try:
            self.database.sign_in_queue(queue_id=queue_id, student_id=self.student_tg_id, lab_id=lab_id)
            return self.database.get_lab(lab_id=lab_id)
        except AssertionError as e:
            raise StudentLabNotFoundException(lab_id)


    def reject_review_queue(self, queue_id: str, lab_id: str) -> Lab:
        self.database.sign_out_queue(queue_id=queue_id, student_id=self.student_tg_id, lab_id=lab_id)
        return self.database.get_lab(lab_id=lab_id)


    def get_current_review_queues(self) -> tp.List[BriefQueue]:
        return self.database.get_student_queues(student_id=self.student_tg_id)


    def get_review_queue_rules(self, queue_id: str) -> tp.List[str]:
        queue_obj = self.database.get_queue(queue_id=queue_id)
        return [t.get_name() for t in self.database.get_comparator(comparator_id=queue_obj.comparator_id).conditions]
