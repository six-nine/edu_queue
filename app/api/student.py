

class Student:

    def __init__(self, student_tg_name):
        self.student_tg_name = student_tg_name
        self.groups = []
        self.review_queues = []


    def join_group(self, group_name, invite_code):
        pass


    def leave_group(self, group_name):
        pass


    def subscribe_review_enroll_start_notifications(self):
        pass


    def unsubscribe_review_enroll_start_notifications(self):
        pass


    def enroll_on_review(self, group_name, review_name):
        pass


    def reject_review(self, group_name, review_name):
        pass


    def get_current_review_queues(self):
        pass


    def get_review_queue_rules(self, review_name):
        pass