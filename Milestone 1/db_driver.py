import pymongo
    
class mongo_instance():
    
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["index_db"]
        self.mytbl = self.db["words"]
        
    def insert(self, new_dict):
        ''' DB SCHEMA REFERENCE

            { "term" : "informatics",
              "postings" : {
                  "0/0" : [tf-idf, tf, {inTitle, inH1, inH2, inBold}],
                  "0/1" : [tf-idf, tf, {inTitle, inH1, inH2, inBold}]
                }
            }
        '''
        self.mytbl.insert_one(new_dict)


    def update(self, old_posting, update_posting):
        ''' Update / add a posting for a term already in the index '''
        
        
        self.mytbl.replace_one(old_posting, update_posting)


    def find_term(self, term):
        ''' Run a query for a term(s) in the index '''

        query = {"term" : term}
        
        return self.mytbl.find_one(query)
    

    def print_objects(self):
        ''' Manual check DB for accuracy '''
        
        for x in self.mytbl.find():
            print(x)

    def del_table(self):
        ''' Drop table when needed '''

        self.mytbl.drop()

