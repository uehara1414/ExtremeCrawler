from queue import PriorityQueue
from urllib.parse import urljoin

import requests

from .exceptions import NotHtmlError
from .crawl_unit import CrawlUnit


class ExtremeCrawler:
    """The information about the one crawl

    url: The url which will be crawled
    origin_url: The url which The url is linked from.
    depth: now depth.
    """


    def __init__(self, domain:str, index:str='/', max_depth:int=1024):
        self.domain = domain
        self.max_depth = max_depth

        self.crawl_queue = PriorityQueue()
        self.crawled_url_set = set()

        if not index.startswith('http'):
            self.index = urljoin(domain, index)
        else:
            self.index = index


    def crawl(self):
        self.crawl_queue.put(CrawlUnit(self.domain, self.index, 0))
        while not self.crawl_queue.empty():
            crawl_unit = self.crawl_queue.get_nowait()

            if crawl_unit.url in self.crawled_url_set:
                continue

            if crawl_unit.depth == self.max_depth:
                self.crawled_url_set.add(crawl_unit.url)
                yield crawl_unit.url
                continue

            links = []
            try:
                links = crawl_unit.get_href_links()
            except NotHtmlError:
                continue
            except requests.ConnectionError:
                print('Connection error has occured. Retry to access {} later.'.format(crawl_unit.url))
                self.crawl_queue.put(CrawlUnit(self.domain, crawl_unit.url, crawl_unit.depth))
            except TimeoutError:
                print('Timeout error has occured. Retry to access {} later.'.format(crawl_unit.url))
                self.crawl_queue.put(CrawlUnit(self.domain, crawl_unit.url, crawl_unit.depth))

            self.crawled_url_set.add(crawl_unit.url)

            for url in links:
                if not url in self.crawled_url_set:
                    self.crawl_queue.put(CrawlUnit(self.domain, url, crawl_unit.depth+1))

            yield crawl_unit.url
