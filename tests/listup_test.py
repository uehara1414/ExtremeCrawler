import unittest
import http.server
import threading
import requests

class StaticServer():

    def __init__(self, port=8000):
        self.port = port
        self.server = threading.Thread(target=self.run_server, daemon=False)
        self.server.start()


    def run_server(self):
        http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler, port=8000)


class ListUpTest(unittest.TestCase):

    def setUp(self):
        self.server = StaticServer(port=8000)




    def test1(self):
        req = requests.get('http://localhost:8000/setup.py')
        print(req.text)

    def tearDown(self):
        self.server.st