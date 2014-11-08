import cookielib
import re
import urllib
import urllib2
import sys

class _NoRedirection(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response

class Grabber:

    _login_url = 'https://keats.kcl.ac.uk/login/index.php'

    _re_course_current_course = re.compile('id=[0-9]+">(.*)</a></p><ul><li class="type_unknown depth_4 collapsed contains_branch" aria-expanded="false"><p class="tree_item branch">')

    def __init__(self, username, password):
        self._username = username
        self._password = password

        self._items = {}

    def _get_page(self, url):
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', self._cookie))
        response = opener.open(url)
        return response.read()

    def _get_urls(self):
        return ['http://keats.kcl.ac.uk/course/view.php?id=22751',
            'http://keats.kcl.ac.uk/course/view.php?id=22743']

    def _do_login(self):
        values = {'username': self._username,
            'password': self._password,
            'rememberusername': 0}

        data = urllib.urlencode(values)
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(_NoRedirection, urllib2.HTTPCookieProcessor(cj))
        response = opener.open(self._login_url, data)
        return response.info().getheader('Set-Cookie')[50:91]

    def _parse_course_page(self, page):
        for line in page.split('\n'):
            if 'Current course' in line:
                course = self._re_course_current_course.search(line).group(1)
                if course not in self._items:
                    self._items[course] = {}

    def do_grab(self):
        self._cookie = self._do_login()

        for url in self._get_urls():
            if '/course/' in url:
                self._parse_course_page(self._get_page(url))

if __name__ == '__main__':
    grabber = Grabber(sys.argv[1], sys.argv[2])
    grabber.do_grab()
    print grabber._items
