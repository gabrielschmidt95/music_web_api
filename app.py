from dash import Dash, html, dcc, dependencies
from assets.styles import *
import dash_bootstrap_components as dbc
from pymongo import MongoClient
from dotenv import load_dotenv
from waitress import serve
import pandas as pd
import os


load_dotenv()

port = int(os.environ.get("PORT", 5000))


CONNECTION_STRING = os.environ['CONNECTION_STRING']
DATABASE = "MEDIA"


class MongoConn:
    def __init__(self, conn_str, database):
        self.conn_str = conn_str
        self.database = database

    def open_conn(self):
        self.conn = MongoClient(self.conn_str)[self.database]

    def collection(self, col):
        return self.conn[col]


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

db = MongoConn(CONNECTION_STRING, DATABASE)
db.open_conn()
data = db.collection("CD").find()
df = pd.DataFrame(list(data))
df.drop('_id', inplace=True, axis=1)

sidebar = html.Div(
    [
        html.H2("Music", className="display-4"),
        html.Hr(),
        html.P(
            "Collection Mananger", className="lead"
        ),
        html.Label("Ano de Lançamento"),
        dcc.Dropdown(
            id="input",
            options=[{'label': str(i), 'value': str(i)}
                     for i in sorted(df['RELEASE_YEAR'].unique())],
            value=''
        ),
        # dbc.Nav(
        #     [
        #         dbc.NavLink("Home", href="/", active="exact"),
        #         dbc.NavLink("Page 1", href="/page-1", active="exact"),
        #         dbc.NavLink("Page 2", href="/page-2", active="exact"),
        #     ],
        #     vertical=True,
        #     pills=True,
        # ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([

    html.Div(id='disco')

], style=CONTENT_STYLE)


app.layout = html.Div(children=[
    sidebar,
    dcc.Loading(content)
])


@app.callback(
    dependencies.Output('disco', 'children'),
    [dependencies.Input('input', 'value')],
    prevent_initial_callback=True)
def update_output(value):
    if value is None or len(value) < 1:
        dff = df
    else:
        dff = df.query(f'RELEASE_YEAR == {value}')
    return dbc.Accordion([dbc.AccordionItem([
        html.H4(data["TITLE"], className="card-title"),
        html.H5(data["ARTIST"], className="card-title"),
        dbc.Row(
            [
                dbc.Col(dbc.Row([html.Div(f'RELEASE YEAR: {data["RELEASE_YEAR"]}')])),
                dbc.Col(html.Div(f'MEDIA: {data["MEDIA"]}')),
                dbc.Col(html.Div(f'PURCHASE: {data["PURCHASE"]}')),
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(f'ORIGIN: {data["ORIGIN"]}')),
                dbc.Col(html.Div(f'IFPI_MASTERING: {data["IFPI_MASTERING"]}')),
                dbc.Col(html.Div(f'IFPI_MOULD: {data["IFPI_MOULD"]}')),
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(f'BARCODE: {data["BARCODE"]}')),
                dbc.Col(html.Div(f'MATRIZ: {data["MATRIZ"]}')),
                dbc.Col(html.Div(f'LOTE: {data["LOTE"]}')),
            ],
            align="start",
        ),

    ], title=f'{data["TITLE"]}',
    ) for data in dff.to_dict('records')])


if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
    #serve(app.server, port=5000)
