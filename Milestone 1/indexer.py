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

    # Database
    db_instance = mongo_instance()
    
    with open("../WEBPAGES_RAW/bookkeeping.json", 'r') as bookkeeping:
        datastore = json.load(bookkeeping)

    for key_pair in datastore:
        print(db_instance.print_objects())
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

                dict_term = db_instance.find_term(word)
                new_term = db_instance.find_term(word)
                
                # If word is not in index, add a new entry
                if dict_term == None:
                    new_dict = {"term" : word, "postings" : {key_pair : [0, 1, True, False, False, False]}}
                    db_instance.insert(new_dict)
                    
                # If word is in index and doesn't have posting, add record for file
                elif key_pair not in dict_term["postings"]:

                    new_term["postings"][key_pair] = [0, 1, True, False, False, False]
                    db_instance.update(dict_term, new_term)
                    
                # If word is in index and has posting, update frequency / tag bool
                else:
                    new_term["postings"][key_pair][1] + 1
                    db_instance.update(dict_term, new_term)
            
        bold = soup.find_all("b")
        for x in bold:
            tokenize(x.get_text())
                            
        h1 = soup.find_all("h1")
        for x in h1:
            tokenize(x.get_text())

        h2 = soup.find_all("h2")
        for x in h2:
            tokenize(x.get_text())
        
        # Remove what was already parsed from the document
        for script in soup(["title","b","h1","h2"]):
            script.extract()
        
        # Tokenize the rest of the text and remove stop_words (~175)  
        main_text = tokenize(soup.get_text())
        lesser_text = [x for x in main_text if x not in stop_words or len(x) > 1]

        html.close()

        count +=1
        print(f'{(count/37500)*100}%')
        print("FILE: {} --------------------------------------".format(key_pair))
        
    
if __name__ == "__main__":
    
    # Run the index
    parse_html()
