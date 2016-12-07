import argparse


def parse_arguments(argv: list):
    parser = argparse.ArgumentParser(description='List up all pages in a website.')
    parser.add_argument('domain',
                        help='The domain whose pages are listed up. example: https://www.google.co.jp/')
    parser.add_argument('--index',
                        help='The path which the search starts. example: /index.html defalut: /', default='/')
    parser.add_argument('--depth',
                        help='search depth', default=1024, type=int)
    parser.add_argument('--image-only',
                        help='Get image\'s url only.', action='store_true', default=False)

    args = parser.parse_args(args=argv)

    return args