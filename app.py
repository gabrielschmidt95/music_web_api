from dash import Dash, html, dcc, Input, Output, callback_context, ALL
from assets.styles import *
from data_center import MongoDBConn
import dash_bootstrap_components as dbc
from json import loads
from dotenv import load_dotenv
import plotly.express as px

import os


load_dotenv()

port = int(os.environ.get("PORT", 5000))


df = MongoDBConn(os.environ['CONNECTION_STRING'],
                 os.environ['DATABASE']).qyery("CD")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


sidebar = html.Div(
    [
        html.H2("Music", className="display-4"),
        html.Hr(),
        html.P("Collection Mananger", className="lead"),
        html.Hr(),
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Lançamento", width=5),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'filter-dropdown',
                                    'index': 'RELEASE_YEAR'
                                },
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(df['RELEASE_YEAR'].unique())],
                                value='',
                                className="me-3"
                            ), width=6
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Label("Media", width=5),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'filter-dropdown',
                                    'index': 'MEDIA'
                                },
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(df['MEDIA'].unique())],
                                value='',
                                className="me-3"
                            ), width=6
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Label("Origem", width=5),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'filter-dropdown',
                                    'index': 'ORIGIN'
                                },
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(df['ORIGIN'].dropna().unique())],
                                value='',
                                className="me-3"
                            ), width=6
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Label("Total de CD\'s", width=5),
                        dbc.Col(
                            dbc.Alert(df.groupby(['MEDIA'])['MEDIA'].count(), color="success", className="me-3"), width=6
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Label("Total Geral", width=5),
                        dbc.Col(
                            dbc.Alert(len(df.index), color="success", className="me-3"), width=6
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dcc.Download(id="download_xlsx"),
                        dbc.Col(
                            dbc.Button("Donwload XLSX", color="success", className="me-1",id="download_xlsx_btn"), width=12
                        ),
                    ],
                    className="g-2",
                ),
                
            ])
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

total_year = dbc.Col(
    dcc.Graph(
        id='total_year_graph',
        figure=px.bar(df.groupby(['RELEASE_YEAR'])['RELEASE_YEAR'].count(
        ),
        labels={
            "index": "Ano",
            "value": "Total"
        },
        title="Totais por Ano",
        text_auto=True,
        height=600
    ).update_layout(showlegend=False,hovermode="x unified")
    .update_traces(hovertemplate='Total: %{y}<extra></extra>')
    ), width=12
)

total_origin = dbc.Col(
    dcc.Graph(
        id='total_origin_graph',
        figure=px.bar(df.groupby(['ORIGIN'])['ORIGIN'].count().sort_values(ascending = False),
        labels={
            "index": "Origem",
            "value": "Total"
        },
        title="Totais por Origem",
        text_auto=True,
        height=600
    ).update_layout(showlegend=False)
    ), width=12
)


content = html.Div([
    dbc.Tabs(
        [
            dbc.Tab(html.Div(id='disco'), label="Lista de Discos"),
            dbc.Tab(total_year, label="Totais por Ano"),
            dbc.Tab(total_origin, label="Totais por Origem"),
        ]
    )
], style=CONTENT_STYLE
)


app.layout = html.Div(children=[
    sidebar,
    dcc.Loading(content)
])


@app.callback(
    Output('disco', 'children'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
    prevent_initial_callback=True)
def update_output(value):
    cxt = callback_context.triggered
    if not any(value):
        dff = df
    else:
        print(value)
        _filter = loads(cxt[0]['prop_id'].split('.')[0])["index"]
        dff = df.query(f'{_filter} == "{cxt[0]["value"]}"')
    return dbc.Accordion([dbc.AccordionItem([
        html.H4(data["TITLE"], className="card-title"),
        html.H5(data["ARTIST"], className="card-title"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Row([html.Div(f'RELEASE YEAR: {data["RELEASE_YEAR"]}')])),
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

@app.callback(
    Output("download_xlsx", "data"),
    Input("download_xlsx_btn", "n_clicks"),
    prevent_initial_call=True,
)
def on_button_click(n):
    if n is None:
        raise ""
    else:
        return dcc.send_data_frame(df.to_excel, "collection.xlsx")

if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
