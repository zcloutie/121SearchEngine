import json
import re

from db_driver import *
from stop_words import get_stop_words
from bs4 import BeautifulSoup


def tokenize(line_of_text):
    ''' Handle the text tokenization'''
    
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

        # Fix broken HTML
        soup.prettify()

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
        main_text = tokenize(soup.get_text())
        lesser_text = [x for x in main_text if x not in stop_words]
        
        # Handle main text for a page
        for word in lesser_text:
            db_ops(word, key_pair, "p")
        
        html.close()

        count +=1
        print(f'{(count/37500)*100}%')
        print("FILE: {} --------------------------------------".format(key_pair))


def db_ops(word, key_pair, tag):
    ''' Do DB operations '''

    # Database
    db_instance = mongo_instance()

    dict_term = db_instance.find_term(word)
    new_term = db_instance.find_term(word)
                
    # If word is not in index, add a new entry
    if dict_term == None:
        new_dict = {"term" : word, "postings" : {key_pair : [0, 1, tag]}}
        db_instance.insert(new_dict)
                    
    # If word is in index and doesn't have posting, add record for file
    elif key_pair not in dict_term["postings"]:

        new_term["postings"][key_pair] = [0, 1, tag]
        db_instance.update(dict_term, new_term)
                    
    # If word is in index and has posting, update frequency / tag
    else:
        new_term["postings"][key_pair][1] += 1
        
        if tag not in new_term["postings"][key_pair]:
            new_term["postings"][key_pair].append(tag)
            
        db_instance.update(dict_term, new_term)
        
    
if __name__ == "__main__":
    
    # Run the index
    parse_html()
