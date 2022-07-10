from pymongo import MongoClient
from bson import ObjectId
import pandas as pd

class MongoDBConn(MongoClient):
    def __init__(self, conn_str, database):
        self.conn_str = conn_str
        self.database = database
        self.open_conn()

    def open_conn(self):
        self.conn = MongoClient(self.conn_str)[self.database]

    def qyery(self, coll, query=""):
        df = pd.DataFrame(list(self.conn[coll].find(query)))
        df["PURCHASE"] = df["PURCHASE"].astype('datetime64[ns]')
        return  df
    
    def find_one(self, coll, id):
        return self.conn[coll].find_one(ObjectId(id))
    
    def replace_one(self, coll, id, replace_data):
        return self.conn[coll].replace_one({"_id":ObjectId(id)}, replace_data) 
    
    def insert_one(self, coll, insert_data):
        return self.conn[coll].insert_one(insert_data) 
    
    def delete_one(self, coll, insert_data):
        return self.conn[coll].delete_one(insert_data) 
