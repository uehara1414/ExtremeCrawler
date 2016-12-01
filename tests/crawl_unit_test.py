import unittest
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from extremecrawler.crawl_unit import CrawlUnit

class CrawlUnitTest(unittest.TestCase):

    def test_constructor(self):
        CrawlUnit("http://www.google.co.jp/", '/', 0)

    def test_accessible(self):
        crawl_unit = CrawlUnit("http://www.google.co.jp/", '/', 0)
        crawl_unit.crawl
        crawl_unit.get_url_if_valid
        crawl_unit.get_link_set

    def test_crawl_valid_html_url(self):
        crawl_unit = CrawlUnit("http://www.google.co.jp/", '/', 0)
        self.assertEqual(crawl_unit.get_url_if_valid(), "http://www.google.co.jp")
        self.assertTrue(len(crawl_unit.get_link_set()) > 0)

    def test_crawl_an_invalid_url(self):
        crawl_unit = CrawlUnit('http://www.google/', '/', 0)
        self.assertEqual(crawl_unit.get_url_if_valid(), '')
        self.assertTrue(crawl_unit.get_link_set() == set())

    def test_crawl_valid_image_url(self):
        crawl_unit = CrawlUnit("https://avatars3.githubusercontent.com/u/15319686", '/', 0)
        self.assertEqual(crawl_unit.get_url_if_valid(), "https://avatars3.githubusercontent.com/u/15319686")
        self.assertEqual(crawl_unit.get_link_set(), set())

    def test_get_href_links(self):
        crawl_unit = CrawlUnit("http://www.google.co.jp/", '/', 0)
        text = "<a href='index.html'></a>"
        soup = BeautifulSoup(text)
        self.assertEqual(crawl_unit._get_href_links(soup), {"http://www.google.co.jp/index.html"})

    def test_get_image_srcs(self):
        crawl_unit = CrawlUnit("http://www.google.co.jp/", '/', 0)
        text = "<img src='/foo.png'>"
        soup = BeautifulSoup(text)
        print(crawl_unit._get_image_srcs(soup))
        self.assertEqual(crawl_unit._get_image_srcs(soup), {"http://www.google.co.jp/foo.png"})