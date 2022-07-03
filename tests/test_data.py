from data_center import MongoDBConn
from dotenv import load_dotenv
from typing import NoReturn
import sys 
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
load_dotenv()

COLUMNS = ('RELEASE_YEAR', 'ARTIST', 'TITLE', 'MEDIA', 'PURCHASE', 'ORIGIN',
       'EDITION_YEAR', 'IFPI_MASTERING', 'IFPI_MOULD', 'BARCODE',
       'MATRIZ', 'LOTE')

def test_data() -> NoReturn:
    df = MongoDBConn(os.environ['CONNECTION_STRING'],
                 os.environ['DATABASE']).qyery("CD")
    assert len(df.columns) == len(COLUMNS)
