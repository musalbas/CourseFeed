import cookielib
import time
import re
import json
import urllib
import urllib2
import sys

import lxml.html

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
        self._items_flat = []

    def _get_page(self, url):
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', self._cookie))
        response = opener.open(url)
        return response.read()

    def _get_course_name_from_page(self, page):
        for line in page.split('\n'):
            if 'Current course' in line:
                course = self._re_course_current_course.search(line).group(1)
                if course not in self._items:
                    self._items[course] = {}

        return course

    def _get_urls(self):
        return ['http://keats.kcl.ac.uk/course/view.php?id=22751',
            'http://keats.kcl.ac.uk/course/view.php?id=22743',
            'http://keats.kcl.ac.uk/mod/forum/view.php?id=719368']

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
        course = self._get_course_name_from_page(page)

        tree = lxml.html.fromstring(page)
        sections = tree.xpath('//h3/text()')

        for section in sections:
            if section not in self._items[course]:
                self._items[course][section] = {}
                self._items[course][section]['course_material'] = {}

        for element in tree.xpath('//a'):
            if element.get('onclick'):
                doc_url = element.get('href')
                doc_name = element.getchildren()[1].text

                for s_index in range(len(sections)):
                    if s_index == len(sections) - 1:
                        doc_section = sections[s_index]

                    if page.index(sections[s_index]) < page.index(doc_name) < page.index(sections[s_index + 1]):
                        doc_section = sections[s_index]
                        break

                if doc_url not in self._items[course][sections[s_index]]:
                    timestamp = int(time.time())
                    self._items[course][sections[s_index]]['course_material'][doc_url] = {
                        'name': doc_name,
                        'time': timestamp
                        }

                    self._items_flat.append({
                            'type': 'course_material',
                            'name': doc_name,
                            'timestamp': timestamp,
                            'course': course,
                            'course_section': sections[s_index],
                            'url': doc_url
                        })

    def _parse_forum_index_page(self, page):
        course = self._get_course_name_from_page(page)

        tree = lxml.html.fromstring(page)
        forum_name = tree.xpath('//div[@class="no-overflow"]/text()')[0]

        trs = tree.xpath('//tr')
        first = True
        for tr in trs:
            if first:
                first = False
                continue

            topic_url = tr.getchildren()[0].getchildren()[0].get('href')
            topic_name = tr.getchildren()[0].getchildren()[0].text
            topic_author = tr.getchildren()[2].getchildren()[0].text
            topic_lastpost = tr.getchildren()[4].getchildren()[2].text
            topic_lastpost = time.mktime(time.strptime(topic_lastpost.split(',')[1].strip(), '%d %b %Y'))
            topic_lastpost = int(topic_lastpost)

            if topic_url not in self._items:
                self._items_flat.append({
                    'type': 'forum_post',
                    'url': topic_url,
                    'name': topic_name,
                    'author': topic_author,
                    'timestamp': topic_lastpost,
                    'forum_name': forum_name
                    })

    def do_grab(self):
        self._cookie = self._do_login()

        for url in self._get_urls():
            if '/course/' in url:
                self._parse_course_page(self._get_page(url))
            elif '/mod/forum/view.php' in url:
                self._parse_forum_index_page(self._get_page(url))

        self._items_flat = sorted(self._items_flat, key=lambda k: k['timestamp'])

if __name__ == '__main__':
    grabber = Grabber(sys.argv[1], sys.argv[2])
    grabber.do_grab()
    print json.dumps(grabber._items_flat)
