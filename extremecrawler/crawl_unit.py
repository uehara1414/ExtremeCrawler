from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from .exceptions import NotHtmlError


class CrawlUnit:

    def __init__(self, base:str, url:str, depth:int):
        """一つのURLに対して実際のリクエストを飛ばし解析を行うクラス

        :param base: ドメイン名など
        :param url: 今回解析するURL
        :param depth: 今の深度
        """
        self.base = base
        self.url = url
        self.depth = depth

        self.content_type = ""
        self.link_set = set()
        self.is_valid = False

    def crawl(self, crawl_html: bool = True):
        """リクエストを飛ばし、結果を返す

        与えられたリンクに対し、まずHEADリクエストを送り、Content-Type を判断する
        Content-Type が text/html 以外なら、スクレピング不可なので自URLを返す。
        Content-Type が text/html であるなら、スクレイピングを実行して全リンクを取得し返す。

        """

        try:
            head_res = requests.head(self.url, timeout=5)
            self.content_type = head_res.headers.get("Content-Type")
        except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
            try:
                head_res = requests.get(self.url, timeout=5)
                self.content_type = head_res.headers.get("Content-Type")
            except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
                return

        self.is_valid = True

        if not self.is_html(head_res) or not crawl_html:
            return

        res = requests.get(self.url, timeout=10)

        soup = BeautifulSoup(res.text, "html.parser")

        self.link_set = self._get_href_links(soup)
        self.link_set.update(self._get_image_srcs(soup))

    def to_abs_path(self, href):
        if href.startswith("http"):
            return href

        if href.startswith("//"):
            if "https://" in self.base:
                return "https:" + href
            else:
                return "http:" + href

        return urljoin(self.base, href)

    def get_url_if_valid(self):
        return self.url if self.is_valid else ''

    def get_link_set(self):
        return self.link_set

    def _get_href_links(self, soup: BeautifulSoup):
        href_set = set()
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if not href:
                continue
            href = self.to_abs_path(href)
            href_set.add(href)
        return href_set

    def _get_image_srcs(self, soup: BeautifulSoup):
        src_set = set()
        for img in soup.find_all("img"):
            src = img.get('src', '')
            if not src:
                continue
            src = self.to_abs_path(src)
            if src.startswith(self.base):
                src_set.add(src)
        return src_set

    @staticmethod
    def is_html(response) -> bool:
        return 'text/html' in response.headers['Content-Type']

    def __lt__(self, other):
        return self.depth < other.depth

    def __le__(self, other):
        return self.depth <= other.depth
