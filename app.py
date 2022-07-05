from dash import Dash, html, dcc, Input, Output, State, callback_context, ALL
from assets.styles import *
from data_center import MongoDBConn
import dash_bootstrap_components as dbc
from json import loads
from dotenv import load_dotenv
import random
import plotly.express as px

import os


load_dotenv()

port = int(os.environ.get("PORT", 5000))


df = MongoDBConn(os.environ['CONNECTION_STRING'],
                 os.environ['DATABASE']).qyery("CD")

app = Dash(__name__, external_stylesheets=[
           dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])


sidebar = dbc.Col(
    [
        html.H2("Music", className="display-4"),
        html.Hr(),
        html.P("Collection Mananger", className="lead"),
        html.Hr(),
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label(" Artista", width=3,
                                  className="bi bi-person"),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'filter-dropdown',
                                    'index': 'ARTIST'
                                },
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(df['ARTIST'].unique())],
                                value=None,
                                clearable=False,
                                optionHeight=40,
                                className="me-3"
                            ), width=9
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Label(" Media", width=3, className="bi bi-vinyl"),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'filter-dropdown',
                                    'index': 'MEDIA'
                                },
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(df['MEDIA'].unique())],
                                value=None,
                                clearable=False,
                                className="me-3"
                            ), width=9
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Label(" Origem", width=3, className="bi bi-house"),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'filter-dropdown',
                                    'index': 'ORIGIN'
                                },
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(df['ORIGIN'].dropna().unique())],
                                value=None,
                                clearable=False,
                                className="me-3"
                            ), width=9
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(
                            [
                                dbc.CardHeader("Total de CD\'s"),
                                dbc.CardBody(
                                    [
                                        html.H5(df.groupby(['MEDIA'])['MEDIA'].count(),
                                                className="card-title"),
                                    ]
                                ),
                            ], color="success", outline=True)
                        ),
                        dbc.Col(dbc.Card(
                            [
                                dbc.CardHeader("Total Geral"),
                                dbc.CardBody(
                                    [
                                        html.H5(len(df.index),
                                                className="card-title"),
                                    ]
                                ),
                            ], color="success", outline=True)
                        ),
                    ],
                    className="g-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dcc.Download(id="download_xlsx"),
                        dbc.Col(
                            dbc.Button("Donwload XLSX", color="success", className="me-1", id="download_xlsx_btn"), width=12
                        ),
                    ],
                    className="g-2",
                ),

            ])
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
        ).update_layout(showlegend=False, hovermode="x unified")
        .update_traces(hovertemplate='Total: %{y}<extra></extra>')
    ), width=12
)

total_origin = dbc.Col(
    dcc.Graph(
        id='total_origin_graph',
        figure=px.bar(df.groupby(['ORIGIN'])['ORIGIN'].count().sort_values(ascending=False),
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
            dbc.Tab([
                html.Div(id='disco'),
                html.Hr(),
                dbc.Row([
                    dbc.Col(
                        dbc.Pagination(
                            id="pagination",
                            max_value=1,
                            fully_expanded=False), width=3
                    )], justify="center"
                )], label="Lista"
            ),
            dbc.Tab(total_year, label="Totais por Ano"),
            dbc.Tab(total_origin, label="Totais por Origem"),
        ]
    )
], style=CONTENT_STYLE
)

modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Header")),
        dbc.ModalBody("This is the content of the modal"),
        dbc.ModalFooter(
            dbc.Button(
                "Save", id="save", className="ms-auto", n_clicks=0
            )
        ),
    ],
    id="modal",
    is_open=False,
)


app.layout = html.Div(children=[
    sidebar,
    modal,
    dcc.Store(id="pagination_contents", data=1),
    dcc.Store(id="filter_contents", data={}),
    dcc.Store(id='df'),
    dcc.Loading(content)
])


@app.callback(
    Output("modal", "is_open"),
    Input({'type': 'edit_button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def toggle_modal(n1):
    cxt = callback_context.triggered
    if not cxt[0]['value']:
        return False
    return True


@app.callback(
    Output('disco', 'children'),
    Output('filter_contents', 'data'),
    Output('pagination', 'max_value'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
    Input('pagination_contents', 'data'),
    State('filter_contents', 'data'),
    prevent_initial_callback=True)
def update_output(value, pagination, _filter):
    cxt = callback_context.triggered
    if not any(value):
        max_index = (len(df.index)/10)
        if len(df.index) > 10:
            dff = df.iloc[(pagination*10)-10:pagination*10]
        else:
            dff = df
    else:
        dff = df
        if cxt[0]['prop_id'].split('.')[0] != "pagination_contents":
            _filter_index = loads(cxt[0]['prop_id'].split('.')[0])["index"]
            _filter[_filter_index] = cxt[0]["value"]
        _query = ""
        for key, value in _filter.items():
            if value.isdigit():
                _query += f"{key} == {value} & "
            else:
                _query += f"{key} == '{value}' & "

        _query = _query[:_query.rfind("&")]
        dff = dff.query(_query)
        max_index = int(len(dff.index)/10)
        if len(dff.index) > 10:
            dff = dff.iloc[(pagination*10)-10:pagination*10]

    accord = dbc.Accordion([dbc.AccordionItem([
        html.H4(f' {data["TITLE"]}', className="card-title bi bi-book"),
        html.H5(f' {data["ARTIST"]}', className="card-title bi bi-person"),
        dbc.Row(
            [
                dbc.Col(html.Div(
                    f' RELEASE YEAR: {data["RELEASE_YEAR"]}', className="bi bi-calendar-event")),
                dbc.Col(
                    html.Div(f' MEDIA: {data["MEDIA"]}', className="bi bi-vinyl")),
                dbc.Col(
                    html.Div(f' PURCHASE: {data["PURCHASE"]}', className="bi bi-cart3")),
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(f' ORIGIN: {data["ORIGIN"]}', className="bi bi-house")),
                dbc.Col(
                    html.Div(f' IFPI_MASTERING: {data["IFPI_MASTERING"]}', className="bi bi-body-text")),
                dbc.Col(
                    html.Div(f' IFPI_MOULD: {data["IFPI_MOULD"]}', className="bi bi-body-text")),
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(f' BARCODE: {data["BARCODE"]}', className="bi bi-body-text")),
                dbc.Col(
                    html.Div(f' MATRIZ: {data["MATRIZ"]}', className="bi bi-body-text")),
                dbc.Col(
                    html.Div(f' LOTE: {data["LOTE"]}', className="bi bi-body-text"))
            ],
            align="start",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    html.I(className="bi bi-pencil"),
                    color="warning",
                    outline=True,
                    className="me-1",
                    id={
                        'type': 'edit_button',
                        'index': f'{random.random()}'
                    },
                ), width=2),
            justify="end",
        ),

    ], title=f'{data["TITLE"]}',
    ) for data in dff.to_dict('records')], start_collapsed=True)
    return accord, _filter, max_index


@app.callback(
    Output("pagination_contents", "data"),
    Input("pagination", "active_page"),
    prevent_initial_call=True
)
def change_page(page):
    if page:
        return page


@app.callback(
    Output("download_xlsx", "data"),
    Input("download_xlsx_btn", "n_clicks"),
    State('filter_contents', 'data'),
    prevent_initial_call=True,
)
def on_button_click(n, _filter):
    if n is None:
        raise ""
    else:
        _query = ''
        for key, value in _filter.items():
            if value.isdigit():
                _query += f"{key} == {value} & "
            else:
                _query += f"{key} == '{value}' & "

        _query = _query[:_query.rfind("&")]
        dff = df.query(_query)
        return dcc.send_data_frame(dff.to_excel, "collection.xlsx")


if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
