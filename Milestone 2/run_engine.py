import json
import re


def tokenize(line_of_text):
    '''Handle the text tokenization'''
    
    # Regex: Replace everything that doesn't start with a word character with a space.
    # This also excludes non-english characters from the line of text.
    token = re.compile('[^a-z0-9]')
    
    return_list = re.sub(token, " ", line_of_text.lower())

    return return_list.split()


def run_search_engine():
    '''Run the search engine'''

    print("We're Booting Up...")
    with open("../index.json", "r") as db:
        full_index = json.load(db)
    
    while True:
        
        user_input = str(input("Please Enter Your Query: "))
        query_cosine_vectors(tokenize(user_input))


def query_cosine_vectors(list_of_query_terms):
    '''Compute the cosine values'''

    for term in list_of_query_terms:
        print(term)

    
if __name__ == "__main__":

    run_search_engine()
