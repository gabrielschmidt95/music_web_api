from os import environ

from dash import dcc, html

from data.data_center import MongoDBConn
from server import app
from src.content import Content
from src.modal import Data_Modal
from src.sidebar import Sidebar


class CollectionAPP:

    def __init__(self):
        self.conn = MongoDBConn(
            environ['CONNECTION_STRING'],
            environ['DATABASE']
        )
        self.sidebar = Sidebar(self.conn)
        self.data_modal = Data_Modal(self.conn)
        self.content = Content(self.conn)
        self.create_layout()
        self.create_callbacks()

    def create_layout(self):
        app.layout = html.Div(children=[
            self.sidebar.layout(),
            self.content.layout(),
            self.data_modal.layout(),
            dcc.Store(id="pagination_contents", data=1),
            dcc.Store(id="filter_contents", data={}),
            dcc.Store(id='df'),
            dcc.Store(id='edit_id'),
            dcc.Store(id='delete_id'),
            dcc.Location(id='url')
        ])

    def create_callbacks(self):
        self.sidebar.callbacks()
        self.data_modal.callbacks()
        self.content.callbacks()

    def run(self):
        app.run_server(debug=True, port=5000)


if __name__ == '__main__':
    CollectionAPP().run()
