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

app.title = 'Music Collection'

sidebar = dbc.Col(
    [
        html.H2("Music", className="display-4"),
        html.Hr(),
        html.P("Collection Mananger", className="lead"),
        html.Hr(),
        dbc.Form(
            [
                html.Div(id="drop"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(
                            [
                                dbc.CardHeader("CD\'s"),
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
                                dbc.CardHeader("LP\'s"),
                                dbc.CardBody(
                                    [
                                        html.H5(len(df.index),
                                                className="card-title"),
                                    ]
                                ),
                            ], color="success", outline=True)
                        ),
                        dbc.Col(dbc.Card(
                            [
                                dbc.CardHeader("DVD\'s"),
                                dbc.CardBody(
                                    [
                                        html.H5(len(df.index),
                                                className="card-title"),
                                    ]
                                ),
                            ], color="success", outline=True)
                        ),
                        dbc.Col(dbc.Card(
                            [
                                dbc.CardHeader("BL\'s"),
                                dbc.CardBody(
                                    [
                                        html.H5(df.groupby(['MEDIA'])['MEDIA'].count(),
                                                className="card-title"),
                                    ]
                                ),
                            ], color="success", outline=True)
                        )
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
        figure=px.bar(df.groupby(['RELEASE_YEAR'])['RELEASE_YEAR'].count(),
                      labels={
            "index": "Ano",
            "value": "Total"
        },
            title="Ano de Lançamento",
            text_auto=True,
            height=600
        ).update_layout(showlegend=False, hovermode="x unified")
        .update_traces(hovertemplate='Total: %{y}<extra></extra>')
    ), width=12
)

total_buy = dbc.Col(
    dcc.Graph(
        id='total_purchase_graph',
        figure=px.bar(df.groupby(df['PURCHASE'].dt.year)['PURCHASE'].count(),
                      labels={
            "index": "Ano",
            "value": "Total"
        },
            title="Ano de Aquisição",
            text_auto=True,
            height=600
        ).update_layout(showlegend=False)
    ), width=12
)


content = html.Div([
    dbc.Tabs(
        [
            dbc.Tab([
                dcc.Loading(html.Div(id='disco')),
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
            dbc.Tab(total_year, label="Ano de Lançamento"),
            dbc.Tab(total_buy, label="Ano de Aquisição"),
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
    content
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
    Output("drop", 'children'),
    Input('filter_contents', 'data'),
    prevent_initial_call=True
)
def toggle_modal(_filter):
    if _filter != {}:
        _query = ""
        for key, value in _filter.items():
            _query += f"{key} == '{value}' & "

        _query = _query[:_query.rfind("&")]
        dff = df.query(_query)
    else:
        dff = df
    return [dbc.Row(
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
                             for i in sorted(dff['ARTIST'].unique())],
                    value=_filter["ARTIST"] if "ARTIST" in _filter else None,
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
                             for i in sorted(dff['MEDIA'].unique())],
                    value=_filter["MEDIA"] if "MEDIA" in _filter else None,
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
                             for i in sorted(dff    ['ORIGIN'].dropna().unique())],
                    value=_filter["ORIGIN"] if "ORIGIN" in _filter else None,
                    className="me-3"
                ), width=9
            ),
        ],
        className="g-2",
    )]


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
    _artist = df.groupby('ARTIST', as_index=False)
    if not any(value):
        if cxt[0]['prop_id'] !='.':
            _filter.pop(loads(cxt[0]['prop_id'].split('.')[0])["index"])
        max_index = int(len(_artist.groups.keys())/10)
        if max_index > 10:
            artists = list(_artist.groups.keys())[
                (pagination*10)-10:pagination*10]
            dff = df.query(
                f"ARTIST == @artists").groupby('ARTIST', as_index=False)
        else:
            dff = df.groupby('ARTIST', as_index=False)
    else:
        dff = df
        if cxt[0]['prop_id'].split('.')[0] != "pagination_contents":
            _filter_index = loads(cxt[0]['prop_id'].split('.')[0])["index"]
            _filter[_filter_index] = cxt[0]["value"]
            _filter = dict((k, v) for k, v in _filter.items() if v is not None)
        _query = ""
        for key, value in _filter.items():
            _query += f"{key} == '{value}' & "

        _query = _query[:_query.rfind("&")]
        _artist = df.query(_query).groupby('ARTIST', as_index=False)
        artists = list(_artist.groups.keys())[(pagination*10)-10:pagination*10]
        dff = df.query(f"ARTIST == @artists").groupby('ARTIST', as_index=False)
        max_index = int(len(_artist.groups.keys())/10)
    print(_filter)
    accord = dbc.Accordion([
        dbc.AccordionItem([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H4(f' {row["TITLE"]}',
                            className="card-title bi bi-book"),
                    html.H5(f' {row["ARTIST"]}',
                            className="card-title bi bi-person"),
                    dbc.Row(
                        [
                            dbc.Col(html.Div(
                                f' RELEASE YEAR: {row["RELEASE_YEAR"]}', className="bi bi-calendar-event")),
                            dbc.Col(
                                html.Div(f' MEDIA: {row["MEDIA"]}', className="bi bi-vinyl")),
                            dbc.Col(
                                html.Div(f' PURCHASE: {row["PURCHASE"]}', className="bi bi-cart3")),
                        ],
                        align="start",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(f' ORIGIN: {row["ORIGIN"]}', className="bi bi-house")),
                            dbc.Col(
                                html.Div(f' IFPI_MASTERING: {row["IFPI_MASTERING"]}', className="bi bi-body-text")),
                            dbc.Col(
                                html.Div(f' IFPI_MOULD: {row["IFPI_MOULD"]}', className="bi bi-body-text")),
                        ],
                        align="start",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(f' BARCODE: {row["BARCODE"]}', className="bi bi-body-text")),
                            dbc.Col(
                                html.Div(f' MATRIZ: {row["MATRIZ"]}', className="bi bi-body-text")),
                            dbc.Col(
                                html.Div(f' LOTE: {row["LOTE"]}', className="bi bi-body-text"))
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

                ], title=f'{row["RELEASE_YEAR"]} - {row["TITLE"]}')
                for row in group.to_dict('records')], start_collapsed=True)
        ], title=name,
        ) for name, group in dff], start_collapsed=True)
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
    prevent_initial_call=True,
)
def on_button_click(n):
    if n is None:
        raise ""
    else:
        return dcc.send_data_frame(df.to_excel, "collection.xlsx")


if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
