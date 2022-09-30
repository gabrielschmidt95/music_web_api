from pymongo import MongoClient
from bson import ObjectId
import pandas as pd
import numpy as np


class MongoDBConn(MongoClient):
    def __init__(self, conn_str, database):
        self.conn_str = conn_str
        self.database = database
        self.open_conn()

    def open_conn(self):
        self.conn = MongoClient(self.conn_str)[self.database]

    def qyery(self, coll, query=""):
        resp = list(self.conn[coll].find(query))
        for r in resp:
            for key, value in r.copy().items():
                if value is None:
                    r[key] = ""

        df = pd.DataFrame(resp)
        if df.empty:
            df = pd.DataFrame(columns=['RELEASE_YEAR', 'ARTIST', 'TITLE', 'MEDIA', 'PURCHASE', 'ORIGIN',
                                       'EDITION_YEAR', 'IFPI_MASTERING', 'IFPI_MOULD', 'BARCODE',
                                       'MATRIZ', 'LOTE'])

        df["PURCHASE"] = df["PURCHASE"].astype('datetime64[ns]')
        df.replace({pd.NaT: None, np.nan: None, "NaT": None, "": None}, inplace=True)
        df["ARTIST"] = df["ARTIST"].astype(str)
        df["TITLE"] = df["TITLE"].astype(str)
        df["MEDIA"] = df["MEDIA"].astype(str)
        df["ORIGIN"] = df["ORIGIN"].astype(str)
        df["BARCODE"] = df["BARCODE"].astype(str)


        return df

    def find_all(self, coll):
        return list(self.conn[coll].find())

    def find_one(self, coll, id):
        return self.conn[coll].find_one(ObjectId(id))
    
    def find_custom(self, coll, field, value):
        return self.conn[coll].find_one({field:value})

    def replace_one(self, coll, id, replace_data):
        return self.conn[coll].replace_one({"_id": ObjectId(id)}, replace_data)

    def insert_one(self, coll, insert_data):
        return self.conn[coll].insert_one(insert_data)

    def delete_one(self, coll, _id):
        deleted_count = self.conn[coll].delete_one({"_id": ObjectId(_id)}).deleted_count
        if not deleted_count:
            deleted_count = self.conn[coll].delete_one({"_id": _id}).deleted_count
        return deleted_count
    
    def insert_many(self, coll, insert_data):
        return self.conn[coll].insert_many(insert_data)
    
    def drop(self, coll):
        return self.conn[coll].drop()

