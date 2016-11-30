import unittest

from extremecrawler import ExtremeCrawler


class CollectTest(unittest.TestCase):

    def test_collected_urls_are_unique(self):
        crawler = ExtremeCrawler('http://socket.io/', max_depth=1)
        url_list = list(crawler.crawl())
        self.assertEqual(len(url_list), len(set(url_list)))


    def test_collected_urls_are_unique_2(self):
        crawler = ExtremeCrawler('http://socket.io/', max_depth=2)
        url_list = list(crawler.crawl())
        print(sorted(url_list))
        self.assertEqual(len(url_list), len(set(url_list)))
