import unittest

from models import HT_MEMBER
from utils import get_video_links
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

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.current_member = HT_MEMBER(*current_login)
        self.current_member.login()

    def test_get_video_links(self):
        # test one with both HQ and LQ
        cliffhanger_links = get_video_links(
            self.current_member,
            'https://www.harmontown.com/2019/12/video-episode-360-cliffhanger/'
        )
        self.assertEqual(
            cliffhanger_links.hq_link,
            'https://download.harmontown.com/video/harmontown-2019-12-02-final.mp4'
        )
        self.assertEqual(
            cliffhanger_links.lq_link,
            'https://download.harmontown.com/video/harmontown-2019-12-02-low.mp4'
        )

        # test with only HQ
        debbie_links = get_video_links(
            self.current_member,
            'https://www.harmontown.com/2014/10/video-episode-117-debbie-request-permission-to-do-dallas/'
        )
        self.assertFalse(debbie_links.lq_link)
        self.assertEqual(
            debbie_links.hq_link,
            'https://download.harmontown.com/video/harmontown-2014-09-21-final.mp4'
        )

    def tearDown(self):
        self.current_member.sess.close()

if __name__ == '__main__':
    unittest.main()
