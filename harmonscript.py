# /usr/bin/env python3
# harmonscript.py - download harmontown video podcasts
import requests
import bs4
import re
from getpass import getpass
from fake_useragent import UserAgent
from clint.textui import progress

# FUNCTION DEFINITIONS
def get_video(title, url, s):
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
        with s.get(video_link[0].get('href'), stream = True) as vidreq:
            with open(title + '.mp4', 'wb') as vidfile:
                total_length = int(vidreq.headers.get('content-length'))
                for chunk in progress.bar(vidreq.iter_content(chunk_size = 1024), expected_size = (total_length/1024) + 1):
                    if chunk:
                        vidfile.write(chunk)
                        print('*', end = '')
            

def get_url(year, month, bpreq, s, titleReg):
   
    blogpage = bs4.BeautifulSoup(bpreq.content, features="html.parser")
    
    # recursively access next page until there are no more pages that month
    pages = blogpage.select('#top > div.x-container.max.width.offset > div > div > ul > li:last-child> a')
    if len(pages) > 0:
        npurl = requests.get(pages[0].get('href'))
        get_url(year, month, npurl, s, titleReg)
    
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
            get_video(title, url, s)

# END FUNCTION DEFINITIONS

# log into harmontown
wp_login = 'https://www.harmontown.com/wp-login.php'
username = input('Enter your Harmontown username: ')
password = getpass()
ua = UserAgent()


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

    # search archives for posts that contain video episodes
    for y in range(2014, 2019):
        for m in range(1, 13):
            bpreq = s.get('https://harmontown.com/' + str(y) + '/' + str(m) + '/')
            if bpreq.status_code == 200:
                print(str(m) + ' ' + str(y))
                get_url(str(y), str(m), bpreq, s, titleReg)
