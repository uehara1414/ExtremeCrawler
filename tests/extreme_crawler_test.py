import unittest
from unittest.mock import MagicMock

import requests

from extremecrawler import ExtremeCrawler

class ExtremeCrawlerTest(unittest.TestCase):

    def test_constructor(self):
        self.assertTrue(isinstance(ExtremeCrawler("http://www.google.co.jp/"), ExtremeCrawler))

    def test_constructor2(self):
        self.assertTrue(isinstance(ExtremeCrawler("http://www.google.co.jp/", index="/"), ExtremeCrawler))

    def test_constructor3(self):
        self.assertTrue(ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1), ExtremeCrawler)

    def test_crawl(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        self.assertTrue(isinstance(crawler, ExtremeCrawler))
        crawler.crawl()

    def test_crawl_with_content_filter(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        urls = list(crawler.crawl(content_filter="text/html"))
        for url in urls:
            res = requests.head(url)
            self.assertTrue("text/html" in res.headers["Content-Type"])

    def test_crawl_with_multi_content_filter(self):
        crawler = ExtremeCrawler("https://github.com/", index="/uehara1414/bakuretsu-mahou/blob/master/README.md", max_depth=1)
        urls = list(crawler.crawl(content_filter=["image", "text/html"]))
        for url in urls:
            res = requests.head(url)
            self.assertTrue("text/html" in res.headers["Content-Type"] or "image" in res.headers["Content-Type"])

    def test_is_already_crawled(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        urls = list(crawler.crawl())
        for url in urls:
            self.assertTrue(url in crawler._is_already_crawled(url))

    def test_filter_crawled_urls(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        filtered = crawler._filter_crawled_urls({"http://www.google.co.jp/", "https://github.com/"})
        self.assertEqual(set(filtered), {"http://www.google.co.jp/"})
