import sys
import urllib
import requests
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser
from collections import deque

link_tag = 'a'
search_attrs = set(['href', 'src'])
agent = 'CerradoBot3000/1.0 (+https://github.com/WalterCJ)'
headers = {'user-agent': agent}
content_type_html = 'html'


class LinkParser(HTMLParser):
    def __init__(self, home):
        super().__init__()
        self.home = home
        self.checked_links = set()
        self.pages_to_check = deque()
        self.pages_to_check.appendleft(home)
        self.scanner()

    def scanner(self):
        while self.pages_to_check:
            url = self.pages_to_check.pop()
            res = requests.get(url, headers=headers)
            if content_type_html in res.headers.get('content-type'):
                self.feed(res.text)  # feed data to parser

    def handle_starttag(self, tag, attrs):
        if tag == link_tag:
            for attr, value in attrs:
                if (attr in search_attrs) and (value not in self.checked_links):
                    self.checked_links.add(value)
                    self.check_link(self.handle_link(value))

    def handle_link(self, url):
        if not bool(urlparse(url).netloc):
            return urljoin(self.home, url)
        else:
            return url

    def check_link(self, url):
        status = None

        try:
            res = requests.get(url, headers=headers)
            status = res.status_code
        except requests.exceptions.HTTPError as err:
            print(f'HTTPError: {status} - {err} - {url}')  # request returned an unsuccessful status code
        except requests.exceptions.ConnectionError as err:
            print(f'ConnectionError: {status} - {err} - {url}')  # DNS failure, refused connection, etc
        except requests.exceptions.Timeout as err:
            print(f'Timeout: {status} - {err} - {url}')
        except requests.exceptions.RequestException as err:
            print(f'RequestException: {status} - {err} - {url}')
        else:
            print(f'{status} - {url}')
        if self.home in url:
            self.pages_to_check.appendleft(url)


LinkParser(sys.argv[1])