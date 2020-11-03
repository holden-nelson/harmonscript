# find_urls.py
# comb through the Harmontown site to find video page urls for each episode

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

if __name__ == '__main__':
    find_urls()

