import json
import re
import math
import numpy as np
import collections

from stop_words import get_stop_words
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity


def tokenize(line_of_text):
    ''' Handle the text tokenization and remove stopwords '''

    # Set stopwords once
    stop_words = get_stop_words('english')
    
    # Regex: Replace everything that doesn't start with a word character with a space.
    # This also excludes non-english characters from the line of text.
    token = re.compile('[^a-z0-9]')
    
    return_list = re.sub(token, " ", line_of_text.lower())
    tokenized_list = return_list.split()

    # Remove stopwords from query
    for x in tokenized_list:
        if x in stop_words:
            del tokenized_list[tokenized_list.index(x)]
            
    return tokenized_list


def run_search_engine():
    ''' Run the search engine '''
    
    while True:

        ''' Ranking Method:
        1. Tokenize User Input & Remove Stopwords
        2. Cosine Similarity w/ Index Elimination
        3. Weight Based on Tags
        4. Return Top 10 results
        '''

        user_input = str(input("\nPlease Enter Your Query: "))
        query_cosine_vectors(tokenize(user_input))
        

def query_cosine_vectors(list_of_query_terms):
    ''' Compute the cosine values for the query '''

    # Store query terms and tf-idf scores for those terms.
    query_dict = {}

    # [lists] of all postings for all query terms
    all_posting = []

    N = 37497
    query_len = len(list_of_query_terms)

    # No Results if there are no query terms
    if query_len == 0:
        print("\nNo Results\n")

    # idf has no effect on one term queries, sort by tf
    elif query_len == 1:
        word = list_of_query_terms[0]
        
        if word in full_index.keys():
            for key_pair in full_index[word]:
                results.append((key_pair, full_index[word][key_pair]["tf-idf"]*tag_weight(full_index[word][key_pair]["tags"])))
            run_interface(results)
            
        else:
            print(f"\nOops! It looks like {word} doesn't exist.\n")
        
    else:

        for words in list_of_query_terms:
            for key_pair in full_index[words]:
                if key_pair not in results:
                    results.append((key_pair, full_index[words][key_pair]["tf-idf"]*tag_weight(full_index[words][key_pair]["tags"])))
                else:
                    for tuples in results:
                        if tuples[0] == key_pair:
                            tuples[1] += full_index[words][key_pair]["tf-idf"]*tag_weight(full_index[words][key_pair]["tags"])
                                                                                         
        run_interface(results)
                
        '''
        # Calculate tf-idf for each query term & generate candidate list.
        for term in list_of_query_terms:
            
            term_freq = list_of_query_terms.count(term)
            idf = math.log(N/(term_freq))
            tf = 1 + math.log(term_freq)
            tf_idf = tf*idf
            
            query_dict[term] = tf_idf
            all_posting.append([x for x in full_index[term]])
            
        candidates = candidate_posting(all_posting, query_len)
        
        # Find the space to input the tf-idf scores in the query vector for the query terms.
        index_keys = len(full_index.keys())
        
        query_vector = np.zeros(index_keys)
        
        for index, term in enumerate(full_index.keys()):
            if term in list_of_query_terms:
                query_vector[index] = query_dict[term]

        doc_and_call(query_vector, candidates)
        '''

def doc_and_call(query_vector, candidate_list):
    ''' Create document vector and write cosines to results '''

    index_keys = len(full_index.keys())

    # Only consider documents that pass as a candidate.
    count = 0
    
    for key_pair in candidate:
        count += 1
        print(f"{(count/len(candidate_list))*100}%")
        
        doc_vector = np.zeros(index_keys)

        for index, term in enumerate(full_index.keys()):
            if key_pair in full_index[term]:
                doc_vector[index] = full_index[term][key_pair]["tf-idf"]

            results.append((key_pair, cosine_similarity_re(query_vector, doc_vector)))
        
    run_interface(results)
        
        
def cosine_similarity_re(query, document):
    ''' return cosine similiarity '''

    # Handles Divide By Zero Error
    if (cosine_normal(query)*cosine_normal(document)) == 0:
        return 0
    
    return (np.dot(query, document))/(cosine_normal(query)*cosine_normal(document))


def cosine_normal(scalar):
    ''' takes scalar and squares it '''
    
    return math.sqrt(np.dot(scalar, scalar))


def candidate_posting(all_postings, len_of_query):
    ''' Returns a candidate list of posting that appear in ~75% of terms '''

    must_appear_in = round(len_of_query*.75)
    counter_dict = {}

    if len_of_query == 1:
        return all_postings[0]

    else:
        
        for lists in all_postings:
            for key_pair in lists:
                if key_pair not in counter_dict.keys():
                    counter_dict[key_pair] = 1
                else:
                    counter_dict[key_pair] += 1

        return_list = []
        for key_pair, count in counter_dict.items():
            if count >= must_appear_in:
                return_list.append(key_pair)

        return return_list


def tag_weight(list_of_tags):
    ''' Take results cosine score and multiply by weight based on tags '''

    multiple = 1
    
    if "title" in list_of_tags:
        multiple += 2.5

    elif "h1" in list_of_tags:
        multiple += 1.5

    elif "h2" in list_of_tags:
        multiple += 1

    elif "b" in list_of_tags:
        multiple += .5
    
    return multiple


def run_interface(result_list):
    ''' Print the results in order '''

    sorted_list = sorted(result_list, key = lambda x : x[1], reverse = True)
    count = 0
          
    for key_pair in sorted_list:
        count += 1
        if count <= 10:
            print(f"Result {count}: {get_title(key_pair[0])}\n{datastore[key_pair[0]]}\n\n")
        
    # Clear for next query
    results.clear()
    

def get_title(key_pair):
    ''' Get the title of a webpage if available '''
    
    html = open("../WEBPAGES_RAW/{}".format(key_pair), "rb")
    soup = BeautifulSoup(html, 'lxml')
    html.close()
    soup.prettify()

    titles = soup.find_all("title")

    if len(titles) >= 1:
        return titles[0].get_text()
    else:
        return ' '
    
    
if __name__ == "__main__":

    results = []
    
    print("We're Booting Up...")
    
    with open("../index.json", "r") as db:
        full_index = json.load(db)

    with open("../WEBPAGES_RAW/bookkeeping.json", 'r') as bookkeeping:
        datastore = json.load(bookkeeping)
        
    run_search_engine()
