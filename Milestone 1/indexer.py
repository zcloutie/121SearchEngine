import json
import re
import sys
import gc

from db_driver import *
from stop_words import get_stop_words
from bs4 import BeautifulSoup

db = {}

def tokenize(line_of_text):
    ''' Handle the text tokenization'''
    
    # Regex: Replace everything that doesn't start with a word character with a space.
    # This also excludes non-english characters from the line of text.
    token = re.compile('[^a-z0-9]')
    split_line = line_of_text.split()
    return_list = []

    for x in split_line:
        string =(re.sub(token, " ", x.lower()))
        string += " "
        for i in string.split():
            return_list.append(i)

    return return_list


def parse_html():
    ''' Parse HTML from bookkeeping.json file'''
    
    # For analytics
    count = 0
    
    # Set stopwords once
    stop_words = get_stop_words('english')
    
    with open("../WEBPAGES_RAW/bookkeeping.json", 'r') as bookkeeping:
        datastore = json.load(bookkeeping)

    for key_pair in datastore:
        
        # Path to file is folder/file (0/100), "rb" -- read/binary.
        html = open("../WEBPAGES_RAW/{}".format(key_pair), "rb")

        # Fastest method to parse is lxml according to documentation.
        soup = BeautifulSoup(html, 'lxml')
        html.close()

        # Fix broken HTML
        try:
            soup.prettify()
        except:
            gc.collect()

        # Find and tokenize titles, bold, h1, and h2 tags.
        titles = soup.find_all("title")
        for x in titles:
            for word in tokenize(x.get_text()):
                db_ops(word, key_pair, "title")
            
        bold = soup.find_all("b")
        for x in bold:
            for word in tokenize(x.get_text()):
                db_ops(word, key_pair, "b")
                            
        h1 = soup.find_all("h1")
        for x in h1:
            for word in tokenize(x.get_text()):
                db_ops(word, key_pair, "h1")

        h2 = soup.find_all("h2")
        for x in h2:
            for word in tokenize(x.get_text()):
                db_ops(word, key_pair, "h2")
        
        # Remove what was already parsed from the document along with css / js
        for script in soup(["title","b","h1","h2","script","table","style"]):
            script.extract()
        
        # Tokenize the rest of the text and remove stop_words (~175)
        p_text = soup.get_text().split()
        for y in p_text:
            main_text = tokenize(y)
            lesser_text = [x for x in main_text if x not in stop_words]
        
        # Handle main text for a page
            for word in lesser_text:
                db_ops(word, key_pair, "p")
        
        
        soup.decompose()
        count +=1
        print(f'{(count/37500)*100}%')
        print("FILE: {} --------------------------------------".format(key_pair))


def db_ops(word, key_pair, tag):
    ''' Do DB operations '''
    
    # If word is not in index, add a new entry
    if word not in db:
        db[word] = {key_pair:{"tags":{tag},"tf":1}}
                    
    # If word is in index and doesn't have posting, add record for file
    elif key_pair not in db[word]:

        db[word][key_pair] = {"tags":{tag}, "tf": 1}
                    
    # If word is in index and has posting, update frequency / tag
    else:

        db[word][key_pair]["tags"].add(tag)
        db[word][key_pair]["tf"] += 1
        
    
if __name__ == "__main__":

    db.clear()
    sys.setrecursionlimit(10000)
    # Run the index
    parse_html()
    f= open("index.txt","w+")
    for word in db:
        df = len(db[word])
        db[word]["df"] = df
        f.write("{}:{}".format(word, db[word]))
    f.close()
    sys.setrecursionlimit(1000)
