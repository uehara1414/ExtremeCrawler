import requests
import re
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from queue import Queue

crawl_queue = Queue()


class CrawlUnit:
    """クロール先の情報を保存するオブジェクト

    url: クロール先URL
    origin_url: 遷移元URL
    depth: 現在の深度
    """
    def __init__(self, url, origin_url, depth):
        self.url = url
        self.origin_url = origin_url
        self.depth = depth

    def __eq__(self, other):
        if self.url == other.url:
            return True
        return False

    def __hash__(self):
        return hash(self.url)

    def __str__(self):
        return "{} <- {}, depth: {}".format(self.url, self.origin_url, self.depth)


def to_abs_path(base: str, link: str) -> str:
    return urljoin(base, link)


def save_information(dest_root: str,
                     url,
                     originurl: str,
                     cnt: int) -> None:
    r = requests.get(url)
    img_file_name = str(cnt).zfill(4) + ".png"
    img_file_path = dest_root + "/img/" + img_file_name
    # phantomjsdriver.get(url)
    # phantomjsdriver.save_screenshot(img_file_path)

    # title = phantomjsdriver.title

def get_html(url):
    r = requests.get(url)
    return r.text


def get_href_links(base: str, html: str, root: str, extract_bad=True) -> set:
    soup = BeautifulSoup(html, "html.parser")
    hrefs = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if href is None:
            continue
        hrefs.append(href)

    links = []
    for href in hrefs:
        if href.startswith("http"):
            links.append(href)
            continue

        if href.startswith("//"):
            if "https://" in root:
                links.append("https:" + href)
            else:
                links.append("http:" + href)
            continue

        links.append(to_abs_path(base, href))

    if extract_bad:
        links = extract_bad_urls(links, base, root)

    return set(links)


def check_suffix(url):
    for suffix in [r"\.pdf", r"\.css", r"\.jpe?g", r"\.png", r"\.gif", r"\.bmp", r"\.tiff?"]:
        if re.search(suffix, url, re.IGNORECASE):
            return True
    return False


def extract_bad_urls(urls: list, base: str, root: str) -> list:
    ret = []
    for url in urls:
        if check_suffix(url):
            continue

        if re.search(r".*javascript:.*", url):
            continue

        if url.startswith(root):
            ret.append(url)

    return ret


def crawl(root: str, url: str, depth: int) -> None:
    crawl_queue.put(CrawlUnit(url, url, 0))
    searched_urlset = set()
    crawled_cnt = 0
    while not crawl_queue.empty():
        crawled_cnt += 1
        unit = crawl_queue.get_nowait()

        print("{}/{}: {}".format(crawled_cnt, crawl_queue.qsize() + crawled_cnt, unit))

        html = get_html(unit.url)
        urls = get_href_links(unit.url, html, root)

        if unit.depth >= depth:
            continue

        for the_url in urls:
            if the_url not in searched_urlset:
                crawl_queue.put(CrawlUnit(the_url, unit.url, unit.depth + 1))
                searched_urlset.add(the_url)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='特定ドメイン以下のリンクを列挙しスクリーンショットを取得します')
    parser.add_argument('domain', help='The domain whose pages are listed up. example: https://www.google.co.jp/')
    parser.add_argument('--start', help='The path which the search starts. example: /index.html defalut: /', default='/')
    parser.add_argument('--depth', help='search depth', default=1024, type=int)

    args = parser.parse_args()

    return args


def init_destination(dest_path: str):
    os.makedirs(dest_path + "/img", exist_ok=True)


def main():
    args = parse_arguments()

    # 保存先ディレクトリの作成
    root = args.domain
    start = to_abs_path(root, args.start)

    try:
        crawl(root, start, args.depth)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
