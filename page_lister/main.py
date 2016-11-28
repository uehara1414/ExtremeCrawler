import requests
import re
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import PriorityQueue, Queue, Empty
from threading import Condition
import threading
import time
import logging


class NotHtmlError(BaseException):
    pass


class NotTheSameDomainError(BaseException):
    pass


class CrawlUnit:

    def __init__(self, base:str, url:str, depth:int):
        self.base = base
        self.url = url
        self.depth = depth


    def get_href_links(self):
        try:
            res = requests.get(self.url)
        except requests.exceptions.InvalidSchema:
            raise NotHtmlError()

        if not self.is_html(res):
            raise NotHtmlError()

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


class Crawler:
    """The information about the one crawl

    url: The url will be crawled
    origin_url: The url which The url linked from.
    depth: now depth.
    """
    crawl_queue = PriorityQueue()
    crawled_queue = Queue()
    crawled_url_set = set()
    set_cv = Condition()
    thread_list = []


    def __init__(self, domain:str, url:str, max_depth:int, thread_num=3):
        self.domain = domain
        self.url = url
        self.max_depth = max_depth
        self.href_links = set()
        self.thread_num = thread_num


    def is_finished(self):
        for t in Crawler.thread_list:
            if t.is_alive():
                return False
        return True


    def run(self) -> None:
        while not Crawler.crawl_queue.empty():
            crawl_unit = Crawler.crawl_queue.get()
            links = []
            try:
                links = crawl_unit.get_href_links()
            except (NotHtmlError, NotTheSameDomainError):
                continue
            except requests.ConnectionError:
                print('Connection error has occured. Retry to access {} later.'.format(crawl_unit.url))
                Crawler.crawl_queue.put(crawl_unit)

            self.add_crawled_url(crawl_unit.url)

            if crawl_unit.depth < self.max_depth:
                for url in links:
                    if url in Crawler.crawled_url_set:
                        continue
                    Crawler.crawl_queue.put(CrawlUnit(self.domain, url, crawl_unit.depth+1))


    def add_crawled_url(self, url:str) -> None:
        with Crawler.set_cv:
            Crawler.crawled_queue.put(url)
            Crawler.crawled_url_set.add(url)


    def start(self):
        Crawler.crawl_queue.put(CrawlUnit(self.domain, self.url, 0))

        for _ in range(self.thread_num):
            t = threading.Thread(target=self.run)
            t.start()
            Crawler.thread_list.append(t)

        while not self.is_finished():
            try:
                yield Crawler.crawled_queue.get(timeout=0.01)
            except (Empty, KeyError):
                continue


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='List up all pages in a website.')
    parser.add_argument('domain', help='The domain whose pages are listed up. example: https://www.google.co.jp/')
    parser.add_argument('--start', help='The path which the search starts. example: /index.html defalut: /', default='/')
    parser.add_argument('--depth', help='search depth', default=1024, type=int)

    args = parser.parse_args()

    return args


def get_links(domain, start, depth=1024):
    return crawl(domain, start, depth)


def main():
    args = parse_arguments()

    root = args.domain
    start = urljoin(root, args.start)

    crawler = Crawler(root, start, args.depth, thread_num=5)

    t1 = time.time()
    for x in crawler.start():
        print(x)
    print(time.time() - t1)