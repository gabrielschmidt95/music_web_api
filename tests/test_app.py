import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from utils.csv_converter import ConvertCSV


def test_styles():
    assert True == True