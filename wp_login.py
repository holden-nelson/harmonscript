from getpass import getpass

def get_credentials():
    username = input('What is your Harmontown username? ')
    password = getpass()

    return (username, password)

def wp_login(s, credentials, login_url):
    username, password = credentials

    payload = {
        'log': username, 'pwd': password,
        'wp-submit': 'Log In', 'redirect-to': ''
    }

    # get login page for initial cookies
    s.get(login_url)

    # post credentials
    login_request = s.post(login_url, data=payload, allow_redirects=False)

    for cookie in login_request.cookies:
        if cookie.name[:16] == 'wordpress_logged':
            # login successful
            return s
        else:
            # login unsuccessful
            raise WPLoginError("Failed to login")

class WPLoginError(Exception):
    pass
