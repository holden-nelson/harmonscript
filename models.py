'''
models.py

This file contains the class definitions and core data structures
used in the program
'''
import requests

from lxml import html

from wp_login import wp_login
from settings import HT_LOGIN_URL


class HT_MEMBER():

    def __init__(self, user=None, passw=None):
        self.user = user
        self.passw = passw
        self.member_status = None
        self.sess = requests.session()

    def login(self):
        self.sess = wp_login(self.sess,
                             (self.user, self.passw),
                             HT_LOGIN_URL)

    def is_current(self):
        '''
        to check if current we'll make a request to a video page
        and see if the vid is available
        '''
        # request
        test_page = self.sess.get('https://www.harmontown.com/2019/12/video-episode-360-cliffhanger/')

        # build tree, search for 'members only' banner
        test_page_tree = html.fromstring(test_page.content)
        memb_only_banner = test_page_tree.xpath('//div[@class="pmpro_content_message"]')

        return len(memb_only_banner) == 0

class HT_EPISODE():

    def __init__(self):
        self.title = None
        self.episode_number = None
        self.date_published = None
        self.video_page_link = None
        self.hq_link = None
        self.hq_size = None
        self.lq_link = None
        self.lq_size = None
        self.aud_link = None
        self.aud_size = None