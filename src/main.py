from selenium import webdriver
import requests
import re
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from queue import Queue
from templates import get_head_template, get_content_template, get_tail_template


crawl_queue = Queue()
phantomjsdriver = None


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


def init_output_html(dest_root: str) -> None:
    head_template = get_head_template()
    with open(dest_root + "/index.html", "w", encoding="utf8") as file:
        file.write(head_template)


def write_one_output(dest_root: str, img_file_name: str, url: str,
                     comment1: str="", comment2: str="") -> None:
    img_file_path = "img/" + img_file_name
    content_template = get_content_template()

    content_template = content_template.replace("img-path", img_file_path)
    content_template = content_template.replace("the-url", url)
    content_template = content_template.replace("comment1", comment1)
    content_template = content_template.replace("comment2", comment2)

    with open(dest_root + "/index.html", "a", encoding="utf8") as file:
        file.write(content_template)


def write_tail(dest_root: str) -> None:
    tail_template = get_tail_template()

    with open(dest_root + "/index.html", "a", encoding="utf8") as file:
        file.write(tail_template)


def save_information(dest_root: str,
                     url,
                     originurl: str,
                     cnt: int) -> None:
    r = requests.get(url)
    img_file_name = str(cnt).zfill(4) + ".png"
    img_file_path = dest_root + "/img/" + img_file_name
    phantomjsdriver.get(url)
    phantomjsdriver.save_screenshot(img_file_path)

    title = phantomjsdriver.title

    write_one_output(dest_root, img_file_name, url,
                     "title: " + title, "statuscode: {}".format(r.status_code))


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


def crawl(dest_root: str, url: str, root: str, depth: int) -> None:
    crawl_queue.put(CrawlUnit(url, url, 0))
    urlset = set()
    crawled_cnt = 0
    while not crawl_queue.empty():
        crawled_cnt += 1
        unit = crawl_queue.get_nowait()

        print("{}/{}: {}".format(crawled_cnt, crawl_queue.qsize() + crawled_cnt, unit))
        save_information(dest_root, unit.url, unit.origin_url, crawled_cnt)

        html = get_html(unit.url)
        urls = get_href_links(unit.url, html, root)

        if unit.depth >= depth:
            continue
        for the_url in urls:
            if the_url not in urlset:
                crawl_queue.put(CrawlUnit(the_url, unit.url, unit.depth + 1))
                urlset.add(the_url)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='特定ドメイン以下のリンクを列挙しスクリーンショットを取得します')
    parser.add_argument("-phantomjs-path", help="PhantomJS バイナリへのパス。パスが通っていれば指定する必要はありません", default=None)
    parser.add_argument('-start', help='出発するURL。', required=True)
    parser.add_argument('-depth', help='探索する深さ。指定しなければ1024(事実上の無限)が指定されます', default=1024, type=int)
    parser.add_argument("-root", help='探索するURLのルート', required=True)
    parser.add_argument("-dest", help="生成先ディレクトリ名。", default="output")

    args = parser.parse_args()

    return args


def init_destination(dest_path: str):
    os.makedirs(dest_path + "/img", exist_ok=True)


def main():
    global phantomjsdriver
    args = parse_arguments()

    # 保存先ディレクトリの作成
    dest_root = args.dest
    init_destination(dest_root)

    index_path = "{}/index.html".format(dest_root)
    img_root_path = "{}/img/".format(dest_root)

    if args.phantomjs_path:
        try:
            phantomjsdriver = webdriver.PhantomJS(args.phantomjs_path)
        except Exception as e:
            print(e)
            print("phantomjs の起動に失敗. -phantomjs-path が正しくない?")
    else:
        try:
            phantomjsdriver = webdriver.PhantomJS()
        except Exception as e:
            print(e)
            print("phantomjs の起動に失敗. -phantomjs-path を設定してください")

    init_output_html(dest_root)

    try:
        crawl(dest_root, args.start, args.root, args.depth)
    except Exception as e:
        print(e)
    finally:
        write_tail(dest_root)
        phantomjsdriver.close()

if __name__ == '__main__':
    main()
