# utils.py
# various utilities used in this project
from collections import namedtuple
import re

import requests
from lxml import html

def find_urls():
    '''
    this function crawls the harmontown site and builds
    a dict of video page urls, where the key is the episode id.
    '''

    vid_page_urls_by_episode = dict()
    pattern = r'\d{3}'
    session = requests.session()

    # free videos
    # start from page 2 and countdown
    for i in range(2, 0, -1):
        # request the page
        video_episode_archive_page = session.get('https://www.harmontown.com/category/freevideos/page/'
                                                 + str(i) + '/')

        # build a tree out of its elements
        video_episode_archive_page_tree = html.fromstring(video_episode_archive_page.content)

        # build a list of the elements that contain links to
        # individual pages
        video_episode_page_links = video_episode_archive_page_tree.xpath('//h2[@class="entry-title"]/a')

        # process each element
        for link in video_episode_page_links:
            # extract episode number from the title
            episode_number = re.findall(pattern, link.text)[0]

            # insert page link by episode number into dict
            vid_page_urls_by_episode[episode_number] = link.get('href')
            print(episode_number, vid_page_urls_by_episode[episode_number])

    # paid videos
    # start from page 23 and countdown
    for i in range(23, 0, -1):
        # request the page
        video_episode_archive_page = session.get('https://www.harmontown.com/category/videos/page/'
                                                 + str(i) + '/')

        # build a tree out of its elements
        video_episode_archive_page_tree = html.fromstring(video_episode_archive_page.content)

        # build a list of the elements that contain links to
        # individual pages
        video_episode_page_links = video_episode_archive_page_tree.xpath('//h2[@class="entry-title"]/a')

        # process each element
        for link in video_episode_page_links:
            # extract episode number from the title
            episode_number = re.findall(pattern, link.text)[0]

            # insert page link by episode number into dict
            vid_page_urls_by_episode[episode_number] = link.get('href')
            print(episode_number, vid_page_urls_by_episode[episode_number])

    return vid_page_urls_by_episode

def get_video_links(member, video_page_url):
    '''
    scrape the video post page for episode download links
    returns a namedtuple of links
    '''

    Links = namedtuple('Links', ['hq_link', 'lq_link'])

    # build tree out of video page elements
    # get list of elements containing download links
    video_page = member.sess.get(video_page_url)
    video_page_tree = html.fromstring(video_page.content)
    video_download_links = video_page_tree.xpath('//center//a')

    # first element is hq download link, always
    hq_link = video_download_links[0].get('href')

    # sometimes there isn't a lq link - but if there is
    # the list will always be length 3 and lq link will
    # be the second element
    lq_link = ''
    if len(video_download_links) == 3:
        lq_link = video_download_links[1].get('href')

    link_tuple = Links(hq_link, lq_link)

    return link_tuple

if __name__ == '__main__':
    find_urls()

