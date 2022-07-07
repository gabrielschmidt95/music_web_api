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
