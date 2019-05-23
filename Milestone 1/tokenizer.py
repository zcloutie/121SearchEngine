import sys
import re
import time


def run_tokenizer(arg):
    '''Main function that opens and iterates through the file, calls tokenize
    and returns output functions'''

    # Complexity - linear
    # 1x : 1.23 sec
    # 2x : 1.86 sec
    # 4x : 3.46 sec
    # 8x : 6.97 sec
    # 16x : 14.21 sec

    start = time.time()
    dic = {}

    # Handle error when file can't be opened.
    try:
        
        with open(arg, 'r') as file:

            # Iterate the file instead of readlines() to ensure large inputs
            # can be read.
            for line in file:
                
                tokenized_line = tokenize(line)
                
                for word in tokenized_line:

                    # Add each word to the dictionary or add 1 to the value if key exists.
                    if word in dic:
                        dic[word] += 1
                    else:
                        dic[word] = 1
                        
        #print_output(dic)
        end = time.time()
        return dic
                        
    except Exception as e:
        
        print("An error occurred in run_program(arg)")

        
def tokenize(line_of_text):
    '''Handle the text tokenization'''
    
    # Regex: Replace everything that doesn't start with a word character with a space.
    # This also excludes non-english characters from the line of text.
    token = re.compile('[^a-z0-9]')
    
    return_list = re.sub(token, " ", line_of_text.lower())

    return return_list.split()


def print_output(dic):
    '''Prints the dictionary in the correct format'''

    # First sort by negation of the 2nd dic value (frequency), then sort alphabetically.
    dic = sorted(dic.items(), key = lambda x: (-x[1], x[0]))

    # For each dic entry, print the key and frequency.
    for x in range(0, len(dic)):
        
        print("{}\t{}".format(dic[x][0], dic[x][1]))
        
    
if __name__ == "__main__":
    '''This instantiates the main thread'''

    # cli$ python {PartA.py} {file.txt} <- file name is the 2nd argument.
    run_program(sys.argv[1])
