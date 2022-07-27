from data.data_center import MongoDBConn
from dotenv import load_dotenv
from typing import NoReturn
import pandera as pa
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
load_dotenv()

validate_schema = pa.DataFrameSchema({
    "RELEASE_YEAR": pa.Column(int),
    "ARTIST": pa.Column(str),
    "TITLE": pa.Column(str),
    "MEDIA": pa.Column(str),
    "PURCHASE": pa.Column(object, nullable=True),
    "ORIGIN": pa.Column(str, nullable=True),
    "EDITION_YEAR": pa.Column(float, nullable=True),
    "IFPI_MASTERING": pa.Column(str, nullable=True),
    "IFPI_MOULD": pa.Column(str, nullable=True),
    "MATRIZ": pa.Column(str, nullable=True),
    "LOTE": pa.Column(str, nullable=True)
})


def test_data() -> NoReturn:
    df = MongoDBConn(os.environ['CONNECTION_STRING'],
                     os.environ['DATABASE']).qyery("CD")
    try:
       validate_schema(df)
    except:
       raise "SCHEMA ERROR"   
