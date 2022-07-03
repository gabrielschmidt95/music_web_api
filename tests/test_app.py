import sys 
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from assets.styles import *

def test_styles():
    assert isinstance(CONTENT_STYLE,dict) == True
    assert isinstance(SIDEBAR_STYLE,dict) == True