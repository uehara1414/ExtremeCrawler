import os
from setuptools import setup


longDesc = ""
if os.path.exists("README.md"):
    longDesc = open("README.md").read().strip()

setup(
    name = "ExtremeCrawler",
    version = "0.1.0",
    author = "uehara1414",
    description = ("List up all pages in a website."),
    long_description = longDesc,
    license = "MIT License",
    keywords = "python scraping web",
    url = "https://github.com/uehara1414/ExtremeCrawler",
    packages=["extremecrawler"],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)