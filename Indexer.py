#https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
import sys
import json
from PartA import tokenize
from bs4 import BeautifulSoup

import atexit
import logging

from crawler import Crawler
from frontier import Frontier

def index():
    index = {}
    with open("WEBPAGES_RAW/bookkeeping.json", 'r') as bookkeeping:
        datastore = json.load(bookkeeping)
    for key in datastore:
        html = open("WEBPAGES_RAW/{}".format(key), "rb")
        soup = BeautifulSoup(html, 'lxml')
        for script in soup(["script","style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        html.close()
        print("FILE: {} --------------------------------------".format(key))
        print(text)

if __name__ == "__main__":
    """# Configures basic logging
    logging.basicConfig(format='%(asctime)s (%(name)s) %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

    # Instantiates frontier and loads the last state if exists
    frontier = Frontier()
    frontier.load_frontier()
    # Registers a shutdown hook to save frontier state upon unexpected shutdown
    atexit.register(frontier.save_frontier)

    # Instantiates a crawler object and starts crawling
    # then gets list of all non-trap urls
    crawler = Crawler(frontier)
    good_urls = crawler.start_crawling()
    for url in good_url:"""
    index()
