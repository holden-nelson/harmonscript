import unittest

from models import HT_MEMBER
from secrets import non_current_login, current_login

class TestModels(unittest.TestCase):

    def setUp(self):
        self.non_current_member = HT_MEMBER(*non_current_login)
        self.non_current_member.login()

        self.current_member = HT_MEMBER(*current_login)
        self.current_member.login()

    def test_is_current(self):
        self.assertFalse(self.non_current_member.is_current())
        self.assertTrue(self.current_member.is_current())

    def tearDown(self):
        self.non_current_member.sess.close()
        self.current_member.sess.close()

if __name__ == '__main__':
    unittest.main()
