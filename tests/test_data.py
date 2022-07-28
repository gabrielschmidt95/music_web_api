from data.data_center import MongoDBConn
from dotenv import load_dotenv
from typing import NoReturn
import pandera as pa
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
load_dotenv()

validate_schema = pa.DataFrameSchema({
    "RELEASE_YEAR": pa.Column(object),
    "ARTIST": pa.Column(object),
    "TITLE": pa.Column(object),
    "MEDIA": pa.Column(object),
    "PURCHASE": pa.Column(object, nullable=True),
    "ORIGIN": pa.Column(object, nullable=True),
    "EDITION_YEAR": pa.Column(object, nullable=True),
    "IFPI_MASTERING": pa.Column(object, nullable=True),
    "IFPI_MOULD": pa.Column(object, nullable=True),
    "MATRIZ": pa.Column(object, nullable=True),
    "LOTE": pa.Column(object, nullable=True)
})


def test_data() -> NoReturn:
    df = MongoDBConn(os.environ['CONNECTION_STRING'],
                     os.environ['DATABASE']).qyery("CD")
    try:
       validate_schema(df)
    except:
       raise "SCHEMA ERROR"   
