from app.models.models import QueueStudent, Comparator, Condition
from app.db.db import Database
from datetime import datetime

def calculateKey(db: Database, comparator: Comparator, group_id: str, student: QueueStudent) -> int:
    def get_val() -> int:
        if condition.c_type == Condition.ConditionType.NUM_OF_ACCEPTED_LABS:
            return db.get_student_passed_labs_count()
        if condition.c_type == Condition.ConditionType.IS_CURRENT_DEALINE_MISSED:
            is_missed = db.get_lab_deadline(lab_id=student.lab_id) < datetime.now()
            return 1 if is_missed else -1
        if condition.c_type == Condition.ConditionType.NUM_OF_ATTEMPTS_BY_CURRENT_LAB:
            return db.get_student_lab_attempts_count(group_id=group_id, lab_id=student.lab_id)
        if condition.c_type == Condition.ConditionType.NUM_OF_MISSED_DEADLINES:
            return db.get_num_of_missed_deadlines(student_id=student.student_id)
        if condition.c_type == Condition.ConditionType.DIFF_BETWEEN_CURRENT_LAB_AND_SUBMITTING:
            return (db.get_lab_deadline(lab_id=student.lab_id) - datetime.now()).total_seconds() / 60 / 60

    res = 0
    for condition in comparator.conditions:
        res *= 10000
        sign = 1 if condition.c_order == Condition.ConditionOrder.ASCENDING else -1

        res += 5000 + sign * get_val()
    return res
