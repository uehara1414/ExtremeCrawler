import unittest

from extremecrawler.parse_arguments import parse_arguments


class ArgparseTest(unittest.TestCase):

    def test_parse_only_domain(self):
        arguments = 'http://www.google.co.jp'.split(' ')
        parsed = parse_arguments(arguments)
        self.assertEqual(parsed.domain, 'http://www.google.co.jp')
        self.assertEqual(parsed.depth, 1024)
        self.assertEqual(parsed.index, '/')

    def test_parse_domain_and_depth(self):
        arguments = 'http://www.google.co.jp --depth 2'.split(' ')
        parsed = parse_arguments(arguments)
        self.assertEqual(parsed.domain, 'http://www.google.co.jp')
        self.assertEqual(parsed.depth, 2)
        self.assertEqual(parsed.index, '/')

    def test_parse_domain_and_index(self):
        arguments = 'http://www.google.co.jp --index index.html'.split(' ')
        parsed = parse_arguments(arguments)
        self.assertEqual(parsed.domain, 'http://www.google.co.jp')
        self.assertEqual(parsed.depth, 1024)
        self.assertEqual(parsed.index, 'index.html')
