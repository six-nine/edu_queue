from app.api.teacher import Teacher
from unittest import TestCase

class TestTeacherApi(TestCase):
    def test_True(self):
        assert True

    def test_api_import(self):
        assert Teacher(0, None) # Warning: Do not rely on this behaviour

    def test_False(self):
        assert False # Remove it later