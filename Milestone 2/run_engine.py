from indexer import tokenize


def run_search_engine():
    '''Run the search engine'''

    db = open("index.json", "r")
    full_index = json.load(db)
    
    while True:
        user_input = input("Please Enter Your Query: ")
        tokenize(user_input)


def query_cosine_vectors(list_of_query_terms):
    '''Compute the cosine values'''
    
if __name__ == "__main__":

    run_search_engine()
