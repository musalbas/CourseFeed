import cookielib
import urllib
import urllib2
import sys

class _NoRedirection(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response

class Grabber:

    _LOGIN_URL = 'https://keats.kcl.ac.uk/login/index.php'

    def __init__(self, username, password):
        self._username = username
        self._password = password

        self._items = {}

    def _get_urls(self):
        return ['http://keats.kcl.ac.uk/course/view.php?id=22751']

    def _do_login(self):
        values = {'username': self._username,
            'password': self._password,
            'rememberusername': 0}

        data = urllib.urlencode(values)
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(_NoRedirection, urllib2.HTTPCookieProcessor(cj))
        response = opener.open(self._LOGIN_URL, data)
        return response.info().getheader('Set-Cookie')[50:91]

    def do_grab(self):
        self._cookie = self._do_login()

        for url in self._get_urls():
            print url

    def get_json(self):
        pass

if __name__ == '__main__':
    grabber = Grabber(sys.argv[1], sys.argv[2])
    grabber.do_grab()
    print grabber.get_json()
