from data.data_center import MongoDBConn
from dotenv import load_dotenv
from typing import NoReturn
import pandera as pa
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
load_dotenv()

validate_schema = pa.DataFrameSchema({
    "RELEASE_YEAR": pa.Column,
    "ARTIST": pa.Column,
    "TITLE": pa.Column,
    "MEDIA": pa.Column,
    "PURCHASE": pa.Column,
    "ORIGIN": pa.Column,
    "EDITION_YEAR": pa.Column,
    "IFPI_MASTERING": pa.Column,
    "IFPI_MOULD": pa.Column,
    "MATRIZ": pa.Column,
    "LOTE": pa.Column
})


def test_data() -> NoReturn:
    df = MongoDBConn(os.environ['CONNECTION_STRING'],
                     os.environ['DATABASE']).qyery("CD")
    try:
       validate_schema(df)
    except:
       raise "SCHEMA ERROR"   
