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

        '''
        count +=1

        if count in [375, 1875, 3750, 7500, 15000, 20000, 25000, 30000, 35000]:
            print(f'{(count/37500)*100}%')
        '''
            

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


        
def tfidf():
    #TF-IDF is TF X IDF
    #TF is the amount of times a term appears divided by the total amount of terms
    #IDF is Log base 10(Total num of docs/number of docs term appears in)
    result = db
    count = 0
    files = {}
    for word in db:
        print(f'{(count/len(db))*100}%')
        idf = math.log(N/len(db[word]),10)
        for doc in db[word].keys():
            if doc not in files:
                files[doc] = total_words(doc)
            tf = db[word][doc]["tf"]/files[doc]
            result[word][doc]["tf-idf"] = tf*idf
        count+=1
    return result
def total_words(key_pair):
    count = 0
    for word in db:
        if key_pair in db[word]:
            count+=db[word][key_pair]["tf"]
    return count

    
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
