import unittest

class GenericTests(unittest.TestCase):

    def test_import(self):
        import page_lister


    def test_accessible(self):
        import page_lister
        page_lister.get_links
