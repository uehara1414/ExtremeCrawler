import sys
from urllib.parse import urljoin

from .extreme_crawler import ExtremeCrawler
from .parse_arguments import parse_arguments


def main():
    args = parse_arguments(sys.argv[1:])

    root = args.domain
    index = urljoin(root, args.index)

    crawler = ExtremeCrawler(root, index=index, max_depth=args.depth)

    for x in crawler.crawl(content_filter="text/html"):
        print(x)

if __name__ == '__main__':
    main()
