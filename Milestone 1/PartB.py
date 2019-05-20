import sys
import re
import itertools as it
import time


def run_program(arg1, arg2):
    '''Main function that opens and iterates through the file, calls tokenize
    and print output functions'''

    # Complexity - Linear
    # 1x : 2.55 sec
    # 2x : 5.31 sec
    # 4x : 10.46 sec
    # 8x : 20.91 sec
    # 16x : 44.06 sec

    start = time.time()
    set1 = set()
    set2 = set()

    # Handle error when file can't be opened.
    try:
        
        with open(arg1, 'r') as file1, open(arg2, 'r') as file2:

            # Iterate each file instead of readlines() to ensure large inputs
            # can be read. izip_longest runs until end of longest file is complete.
            for line1, line2 in it.izip_longest(file1, file2):
                
                tokenized_line = tokenize(str(line1), str(line2))
                
                for word1, word2 in it.izip_longest(tokenized_line[0], tokenized_line[1]):

                    # Add each word to the respective set. Sets eliminate duplicate tokens.
                    set1.add(word1)
                    set2.add(word2)

        # Some cases had None in the set
        if None in set1:
            set1.remove(None)
        
        # Print the length of the intersection of the two sets
        print(len(set1 & set2))
        end = time.time()
                        
    except Exception as e:
        
        print("An error occurred in run_program(arg)")

        
def tokenize(line_of_text1, line_of_text2):
    '''Handle the text tokenization'''
    
    # Regex: Replace everything that doesn't start with a word character with a space.
    # This also excludes non-english characters from the line of text.
    token = re.compile('[^a-z0-9]')
    
    return_list1 = str(re.sub(token, " ", line_of_text1.lower()))
    return_list2 = str(re.sub(token, " ", line_of_text2.lower()))

    return (return_list1.split(), return_list2.split())
        
    
if __name__ == "__main__":
    '''This instantiates the main thread'''

    # cli$ python {PartB.py} {file.txt} {file.txt}<- file names are 2nd/3rd argument.
    run_program(sys.argv[1], sys.argv[2])
