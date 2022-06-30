from pymongo import MongoClient
from dotenv import load_dotenv
from dash import Dash, html, dcc, dependencies, dash_table
from dash.exceptions import PreventUpdate
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


app = Dash(__name__)

db = MongoConn(CONNECTION_STRING, DATABASE)
db.open_conn()
data = db.collection("CD").find()
df = pd.DataFrame(list(data))
df.drop('_id', inplace=True, axis=1)

app.layout = html.Div(children=[
    html.H1(children='MUSIC COLLECTION MANANGER'),
    html.Label("Ano de Lançamento"),
    dcc.Dropdown(
        id="input",
        options=[{'label': str(i), 'value': str(i)}
                 for i in sorted(df['RELEASE_YEAR'].unique())],
        value=''
    ),

    html.Div(id='disco', children=[dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records')
    )])

])


@app.callback(
    dependencies.Output('disco', 'children'),
    [dependencies.Input('input', 'value')],
    prevent_initial_callback=True)
def update_output(value):
    if value is None or len(value) < 1:
        table = dash_table.DataTable(
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records')
        )
        return table
    else:
        print(f"value{type(value)}")
        dff = df.query(f'RELEASE_YEAR == {value}')
        table = dash_table.DataTable(
            columns=[{'name': i, 'id': i} for i in dff.columns],
            data=dff.to_dict('records')
        )
        return table


if __name__ == '__main__':
    # app.run_server(debug=True)
    serve(app.server, listen='*:{port}')
