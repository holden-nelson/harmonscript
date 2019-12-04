# /usr/bin/env python3
# harmonscript.py - download harmontown video podcasts
import json
from os.path import abspath, join, exists
from time import sleep

import requests
import bs4
import re
from getpass import getpass
from fake_useragent import UserAgent
from clint.textui import progress

INVENTORY = {
    'completed': [],
}
INVENTORY_PATH = './.inventory.json'


def load_inventory(dir_path):
    """
    load an inventory file if present, or create it if missing
    :param dir_path: target directory
    """
    global INVENTORY
    global INVENTORY_PATH
    inventory_path = join(abspath(dir_path), ".inventory.json")
    if exists(inventory_path):
        with open(inventory_path, "r") as inv_file:
            INVENTORY = json.load(inv_file)
    else:
        with open(inventory_path, "w") as inv_file:
            json.dump(INVENTORY, inv_file)
    INVENTORY_PATH = inventory_path


def save_inventory():
    with open(INVENTORY_PATH, 'w') as inv_file:
        json.dump(INVENTORY, inv_file)

# FUNCTION DEFINITIONS
def get_video(title, url, s, destination_dir=None):
    global INVENTORY
    vpreq = s.get(url)
    vidpage = bs4.BeautifulSoup(vpreq.content, features="html.parser")
    
    # Episode 263 has a different identifier 
    if url != 'https://www.harmontown.com/2017/10/video-episode-263-seventeen-chicken-boots/':
        video_link = vidpage.select('.x-responsive-video a')
    else:
        video_link = vidpage.select('.x-responsive-audio-embed a')

    if len(video_link) > 0:
        print(video_link[0].get('href'))
    else:
        video_link = vidpage.select('.entry-content a')
        if len(video_link) > 0:
            print(video_link[0].get('href'))
        else:
            print('Video element not found')

    if len(video_link) > 0:
        target_dir = destination_dir or abspath(".")

        with s.get(video_link[0].get('href'), stream = True) as vidreq:
            target_file_name = title + '.mp4'
            if target_file_name in INVENTORY['completed']:
                print('Already completed, skipping...')
                return
            target_file = join(target_dir, target_file_name)
            with open(target_file, 'wb') as vidfile:
                total_length = int(vidreq.headers.get('content-length'))
                for chunk in progress.bar(vidreq.iter_content(chunk_size = 1024), expected_size = (total_length/1024) + 1):
                    if chunk:
                        vidfile.write(chunk)
            INVENTORY['completed'].append(target_file_name)
            save_inventory()
        sleep(2)  # let the server breathe
            

def get_url(year, month, bpreq, s, titleReg, destination_dir=None):
   
    blogpage = bs4.BeautifulSoup(bpreq.content, features="html.parser")
    
    # recursively access next page until there are no more pages that month
    pages = blogpage.select('#top > div.x-container.max.width.offset > div > div > ul > li:last-child> a')
    if len(pages) > 0:
        npurl = requests.get(pages[0].get('href'))
        get_url(year, month, npurl, s, titleReg, destination_dir)
    
    # find elements that contain videos
    if year == '2014':
        vid_post_elems = blogpage.select('.format-video .entry-title a')   
    else:    
        vid_post_elems = blogpage.select('.category-videos .entry-title a')
    
    if len(vid_post_elems) > 0:
        for vid_post in vid_post_elems:
            title = titleReg.sub('', vid_post.get('title')[14:])
            url = vid_post.get('href')
            print(title + ' - ' + url)
            get_video(title, url, s, destination_dir)

# END FUNCTION DEFINITIONS

# log into harmontown
wp_login = 'https://www.harmontown.com/wp-login.php'
username = input('Enter your Harmontown username: ')
password = getpass()
ua = None
try:
    ua = UserAgent()
except Exception as ex:
    # UserAgent can spit an ugly traceback users don't care about
    pass


with requests.Session() as s:
    headers = {
        'User-Agent': str(ua.chrome),
        'Referer': wp_login,
        'Cookie': 'wordpress_test_cookie=WP+Cookie+check'
    }
    
    payload = { 
        'log': username, 'pwd': password, 'wp-submit': 'Log In',
        'redirect-to': '', 'testcookie': '1'
    }

    # get login page for initial cookies
    s.get(wp_login, headers = headers)

    # post credentials to wp_login
    login_req = s.post(wp_login, data = payload, headers = headers, allow_redirects = False)

    # check if successful

    # make regex to match illegal characters in title
    titleReg = re.compile(r'[:<>"/\|?*]')

    # users choose dates to download
    print('Choose archives to fetch videos from')
    print('Video episodes begin in October 2014')

    startm = input('Start month (1 to 12): ')
    starty = input('Start year (2014 to 2019): ')
    endm = input('End month (1 to 12): ')
    endy = input('End year (2014 to 2019): ')
    location = input('Destination folder (default is current): ')

    if not exists(abspath(location)):
        print("Invalid folder: " + location)
        exit(1)
    load_inventory(location)

    if (int(endy) - int(starty)) != 0:

        for m in range(int(startm), 13):
            bpreq = s.get('https://harmontown.com/' + starty + '/' + str(m) + '/')
            if bpreq.status_code == 200:
                print(str(m) + ' ' + starty)
                get_url(starty, str(m), bpreq, s, titleReg, location)

        while (int(starty) + 1) != int(endy):
            starty = str(int(starty) + 1)
            for m in range(1, 13):
                bpreq = s.get('https://harmontown.com/' + starty + '/' + str(m) + '/')
                if bpreq.status_code == 200:
                    print(str(m) + ' ' + starty)
                    get_url(starty, str(m), bpreq, s, titleReg, location)

        for m in range(1, int(endm)):
            bpreq = s.get('https://harmontown.com/' + endy + '/' + str(m) + '/')
            if bpreq.status_code == 200:
                print(str(m) + ' ' + endy)
                get_url(endy, str(m), bpreq, s, titleReg, location)
    
    else:
        for m in range(int(startm), (int(endm)+1)):
            bpreq = s.get('https://harmontown.com/' + endy + '/' + str(m) + '/')
            if bpreq.status_code == 200:
                print(str(m) + ' ' + endy)
                get_url(endy, str(m), bpreq, s, titleReg, location)
