from pymongo import MongoClient
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
        df.drop('_id', inplace=True, axis=1)
        return  df
