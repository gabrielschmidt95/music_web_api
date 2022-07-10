from dash import html, dcc
from data.data_center import MongoDBConn
from dotenv import load_dotenv
from os import environ
from server import app
from src.sidebar import Sidebar
from src.content import Content
from src.data_modal import Data_Modal
from utils.downloads import Downloads

load_dotenv()

class CollectionAPP:

    def __init__(self):
        self.conn = MongoDBConn(
            environ['CONNECTION_STRING'],
            environ['DATABASE']
        )
        self.df = self.conn.qyery("CD")
        self.sidebar = Sidebar(self.df)
        self.data_modal = Data_Modal(self.df, self.conn)
        self.downloads = Downloads(self.df)
        self.create_layout()
        self.create_callbacks()

    def create_layout(self):
        app.layout = html.Div(children=[
            self.sidebar.render(),
            html.Div(id='modal'),
            dcc.Store(id="pagination_contents", data=1),
            dcc.Store(id="filter_contents", data={}),
            dcc.Store(id='df'),
            Content(self.df).content()
        ])
    
    def create_callbacks(self):
        self.sidebar.filters()
        self.data_modal.render()
        self.downloads.xlsx()

    def run(self):
        app.run_server(debug=True, port=5000)

if __name__ == '__main__':
    CollectionAPP().run()
