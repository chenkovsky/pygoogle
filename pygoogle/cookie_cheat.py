#! /usr/bin/env python3
from http.cookiejar import LWPCookieJar, Cookie
import sqlite3
import os.path
import glob
import urllib.parse
import keyring
import sys
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import json
import time

def chrome_cookies(url, path=None):

    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16

    def chrome_decrypt(encrypted_value, key=None):

        # Encrypted cookies should be prefixed with 'v10' according to the
        # Chromium code. Strip it off.
        encrypted_value = encrypted_value[3:]

        # Strip padding by taking off number indicated by padding
        # eg if last is '\x0e' then ord('\x0e') == 14, so take off 14.
        # You'll need to change this function to use ord() for python2.
        def clean(x):
            return x[:-x[-1]].decode('utf8')

        cipher = AES.new(key, AES.MODE_CBC, IV=iv)
        decrypted = cipher.decrypt(encrypted_value)

        return clean(decrypted)

    # If running Chrome on OSX
    if sys.platform == 'darwin':
        my_pass = keyring.get_password('Chrome Safe Storage', 'Chrome')
        my_pass = my_pass.encode('utf8')
        iterations = 1003
        if path is None:
            cookie_file = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')
        else:
            cookie_file = path

    # If running Chromium on Linux
    elif sys.platform == 'linux':
        my_pass = 'peanuts'.encode('utf8')
        iterations = 1
        if path is None:
            cookie_file = os.path.expanduser('~/.config/chromium/Default/Cookies')
        else:
            cookie_file = path
    else:
        raise Exception("This script only works on OSX or Linux.")

    # Generate key from values above
    key = PBKDF2(my_pass, salt, length, iterations)

    # Part of the domain name that will help the sqlite3 query pick it from the Chrome cookies
    domain = urllib.parse.urlparse(url).netloc
    domain_no_sub = '.'.join(domain.split('.')[-2:])

    conn = sqlite3.connect(cookie_file)
    sql = 'select name, value, encrypted_value from cookies '\
            'where host_key like "%{}%"'.format(domain_no_sub)

    cookies = {}
    cookies_list = []

    with conn:
        for k, v, ev in conn.execute(sql):

            # if there is a not encrypted value or if the encrypted value
            # doesn't start with the 'v10' prefix, return v
            if v or (ev[:3] != b'v10'):
                cookies_list.append((k, v))
            else:
                decrypted_tuple = (k, chrome_decrypt(ev, key=key))
                cookies_list.append(decrypted_tuple)
        cookies.update(cookies_list)

    return cookies

def firefox_cookies(url, path=None):
    def find_cookie_file():
        if sys.platform == 'darwin':
            cookie_files = glob.glob(os.path.expanduser('~/Library/Application Support/Firefox/Profiles/*.default*/cookies.sqlite'))
        elif sys.platform.startswith('linux'):
            cookie_files = glob.glob(os.path.expanduser('~/.mozilla/firefox/*.default*/cookies.sqlite'))
        else:
            raise Exception('Unsupported operating system: ' + sys.platform)
        if cookie_files:
            return cookie_files[0]
        else:
            raise Exception('Failed to find Firefox cookie')

    def load(path, domain):
        conn = sqlite3.connect(path)
        #cur = con.cursor()
        with conn:
            #'select host, path, isSecure, expiry, name, value from moz_cookies where host="%{}%"
            cookies = {k: v for k,v in conn.execute('select name, value from moz_cookies where host like "%{}%"'.format(domain))}
        return cookies

    def load_session(path, domain):
        if os.path.exists(path):
            try:
                json_data = json.loads(open(path, 'r').read())
            except ValueError as e:
                print('Error parsing firefox session JSON:', str(e))
            else:
                expires = str(int(time.time()) + 3600 * 24 * 7)
                cookies = {cookie.get('name', ''): cookie.get('value', '')
                 for window in json_data.get('windows', [])
                 for cookie in window.get('cookies', [])
                 if domain == cookie.get('host')}
                return cookies
        else:
            print('Firefox session filename does not exist:%s'% path)

        return {}

    if path is None:
        path = find_cookie_file()
    session_path = os.path.join(os.path.dirname(path), 'sessionstore.js')
    domain = urllib.parse.urlparse(url).netloc
    cookie = load(path, domain)
    session_cookie = load_session(session_path, domain)
    cookie.update(session_cookie)
    return cookie





if __name__ == '__main__':
    from docopt import docopt
    doc = """
export given url's cookie, format only supports "chrome" and "firefox".
if path is "-" then use default cookie. output format is json
Usage:
    cookie_cheat.py <dst> <src> <format> <url>
    """
    args = docopt(doc, version="cookie_cheat v1.0")
    src = None if args["<src>"] == "-" else args["<src>"]
    if args["<format>"] == "chrome":
        cookie = chrome_cookies(args["<url>"], src)
    elif args["<format>"] == "firefox":
        cookie = firefox_cookies(args["<url>"], src)
    with open(args["<dst>"],"w") as fo:
        json.dump(cookie,fo)


