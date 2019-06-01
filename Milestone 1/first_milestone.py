import json
import math

def first_milestone():
    ''' Run this in the shell to input basic queries to get results '''

    with open("../index.json", "r") as db:
        full_index = json.load(db)

    with open("../WEBPAGES_RAW/bookkeeping.json", 'r') as bookkeeping:
        datastore = json.load(bookkeeping)

    print(f"Number of Documents: {37497}")
    print(f"Number of Terms: {len(full_index.keys())}")
    print(f"Index Size (KB): {sys.getsizeof(full_index)/1000}")

    while True:
    
        user_input = input("Please input a simple query: ")
        key_pair_dic = full_index[user_input]
                       
        count = 0
        
        # Only need links for first 20.
        for key in key_pair_dic.keys():
            count += 1
            if count <= 20:
                print(f"{count} : {datastore[key]}")
                
        print(f"{count}\n")

            
        
