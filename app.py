from os import environ

from dash import dcc, html

from server import app
from src.content import Content
from src.modal import DataModal
from src.sidebar import Sidebar


class CollectionAPP:

    def __init__(self):
        self.sidebar = Sidebar()
        self.data_modal = DataModal()
        self.content = Content()
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
        app.run_server(debug=True, port=8050)


if __name__ == '__main__':
    CollectionAPP().run()
