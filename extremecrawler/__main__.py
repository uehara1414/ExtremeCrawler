import argparse
from urllib.parse import urljoin

from .extreme_crawler import ExtremeCrawler



def parse_arguments():
    parser = argparse.ArgumentParser(description='List up all pages in a website.')
    parser.add_argument('domain', help='The domain whose pages are listed up. example: https://www.google.co.jp/')
    parser.add_argument('--start', help='The path which the search starts. example: /index.html defalut: /', default='/')
    parser.add_argument('--depth', help='search depth', default=1024, type=int)

    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    root = args.domain
    start = urljoin(root, args.start)

    crawler = ExtremeCrawler(root, index=start, max_depth=args.depth)

    for x in crawler.crawl():
        print(x)


if __name__ == '__main__':
    main()
