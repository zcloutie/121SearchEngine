import json
import re
import sys
import gc
import math

from stop_words import get_stop_words
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation

db = {}

#Number of files in corpus
N = 37497

def tokenize(line_of_text):
    '''Handle the text tokenization'''
    
    # Regex: Replace everything that doesn't start with a word character with a space.
    # This also excludes non-english characters from the line of text.
    token = re.compile('[^a-z0-9]')
    
    return_list = re.sub(token, " ", line_of_text.lower())

    return return_list.split()


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

        if count in [375, 1875, 3750, 7500, 15000, 20000, 25000, 30000, 35000]:
            print(f'{(count/37500)*100}%')

    update_index_tfidf()
            
    
    
def update_index_tfidf():
    ''' Update the index with tf-idf '''

    N = 37497

    for term, postings in db.items():
        term_idf = math.log(N/len(postings))
        for key_pair in postings:
            tf = 1 + math.log(db[term][key_pair]["tf"])
            tf_idf = tf*term_idf
            db[term][key_pair]["tf-idf"] = tf_idf


def db_ops(word, key_pair, tag):
    ''' Do DB operations '''
    
    # If word is not in index, add a new entry
    if word not in db:
        db[word] = {key_pair:{"tags":[tag],"tf": 1, "tf-idf" : 0}}
                    
    # If word is in index and doesn't have posting, add record for file
    elif key_pair not in db[word]:

        db[word][key_pair] = {"tags":[tag], "tf": 1, "tf-idf" : 0}
                    
    # If word is in index and has posting, update frequency / tag
    else:

        if tag not in db[word][key_pair]["tags"]:
            db[word][key_pair]["tags"].append(tag)
        db[word][key_pair]["tf"] += 1
        

    
if __name__ == "__main__":

    sys.setrecursionlimit(10000)
    
    # Builds db from corpus.
    parse_html()

    # Open and dump db dictionary into index.json.
    f = open("index.json","w")
    print("dumping json")
    json.dump(db,f)
    
    f.close()
    sys.setrecursionlimit(1000)
