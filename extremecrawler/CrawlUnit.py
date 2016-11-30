from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from exceptions import NotHtmlError


class CrawlUnit:

    def __init__(self, base:str, url:str, depth:int):
        self.base = base
        self.url = url
        self.depth = depth


    def get_href_links(self):
        try:
            res = requests.head(self.url)
        except requests.exceptions.InvalidSchema:
            raise NotHtmlError()

        if not self.is_html(res):
            raise NotHtmlError()

        res = requests.get(self.url, timeout=10)


        soup = BeautifulSoup(res.text, "html.parser")
        hrefs = []
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if not href:
                continue
            hrefs.append(href)

        link_set = set()
        for href in hrefs:
            href = self.to_abs_path(href)
            if href.startswith(self.base):
                link_set.add(href)

        return link_set


    def to_abs_path(self, href):
        if href.startswith("http"):
            return href

        if href.startswith("//"):
            if "https://" in self.base:
               return "https:" + href
            else:
                return "http:" + href

        return urljoin(self.base, href)


    def is_html(self, response) -> bool:
        return 'text/html' in response.headers['Content-Type']


    def __lt__(self, other):
        return self.depth < other.depth


    def __le__(self, other):
        return self.depth <= other.depth
