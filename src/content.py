from dash import html, dcc, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
from src.track import Track
from server import app
from json import loads
from os import environ
import requests
from io import StringIO, BytesIO
from server import app
import pandera as pa
import pandas as pd
import numpy as np
import base64


class Content:

    def __init__(self, conn):
        self.conn = conn
        self.MAX_INDEX = 3
        self.track = Track(self.conn)
        self.discogs_url = "https://api.discogs.com/database/search"

    def discogs_get_url(self, row):
        if "DISCOGS" not in row or row["DISCOGS"] is None or "tracks" not in row["DISCOGS"]:
            params = {
                "token": environ["DISCOGS_TOKEN"],
                "artist": row["ARTIST"].lower() if not None else "",
                "release_title": row["TITLE"].lower() if row["TITLE"].lower() is not None else "",
                "barcode": str(row["BARCODE"]) if row["BARCODE"] is not None and row["BARCODE"] != 'None' else "",
                "country": row["ORIGIN"].lower() if not None and row["ORIGIN"].lower() != 'none' else "",
                "year": str(row["RELEASE_YEAR"]) if not None else "",
                "format": "album"
            }
            resp = requests.get(self.discogs_url, params=params)
            if resp.status_code == 200:
                result = resp.json()
                if "results" not in result:
                    return html.Div("Nao encontrado no Discogs")
                result = result["results"]
                if len(result) == 0:
                    params.pop("format")
                    resp = requests.get(self.discogs_url, params=params)
                    result = resp.json()["results"]
                    if len(result) == 0:
                        params.pop("year")
                        resp = requests.get(self.discogs_url, params=params)
                        result = resp.json()["results"]
                        if len(result) == 0:
                            params.pop("country")
                            resp = requests.get(
                                self.discogs_url, params=params)
                            result = resp.json()["results"]
                            if len(result) == 0:
                                params.pop("barcode")
                                resp = requests.get(
                                    self.discogs_url, params=params)
                                result = resp.json()["results"]

                if len(result) > 0:
                    row["DISCOGS"] = result[0]
                    row["DISCOGS"]["urls"] = [
                        {"id": r['id'], "uri": r['uri']} for r in result]
                    row["DISCOGS"]["len"] = len(result)
                    _id = row["DISCOGS"]['id']
                    _type = row["DISCOGS"]['type']
                    tracks = requests.get(
                        f"https://api.discogs.com/{_type}s/{_id}")
                    if tracks.status_code == 200:
                        row["DISCOGS"].update(
                            tracks=tracks.json()["tracklist"])

                    self.conn.replace_one("CD", row["_id"], row)
                else:
                    return html.Div("Nao encontrado no Discogs")
            else:
                return html.Div(f"Error:{resp.status_code}")

        if "tracks" in row["DISCOGS"]:
            tracklist = row["DISCOGS"]["tracks"]
        else:
            tracklist = []

        return dbc.Row([
            dbc.Col([
                dbc.Row(html.Img(
                    src=row["DISCOGS"]['cover_image']
                ), justify="center")
            ], width=4, align="center"),
            dbc.Col([
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                dbc.ListGroup([
                                    dbc.ListGroupItem(dbc.CardLink(
                                        f'DISCOGS - {url["id"]}',
                                        href=f"https://www.discogs.com{url['uri']}",
                                        className="bi bi-body-text",
                                        external_link=True,
                                        target="_blank"
                                    )) for url in row["DISCOGS"]["urls"]
                                ]),
                            ],
                            title=f"ARTIGOS ENCONTRADOS: {row['DISCOGS']['len']}",
                        ),
                    ], start_collapsed=True,
                ),
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                dbc.ListGroup(
                                    [
                                        dbc.ListGroupItem(
                                            f'{t["position"]} - {t["title"]}'
                                        ) for t in tracklist
                                    ]
                                )
                            ],
                            title="Lista de Faixas",
                        ),
                    ], start_collapsed=True,
                ),

            ], width=8)

        ])

    def layout(self):
        return html.Div([
            dcc.Download(id="download_xlsx"),
            html.Div(id="download_alert"),
            html.Div(id="upload_alert"),
            dbc.Row([
                    dbc.Col(
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    " Download XLSX",
                                    color="primary",
                                    className="bi bi-download",
                                    outline=True,
                                    id="download_xlsx_btn"
                                ),
                                dcc.Upload(
                                    dbc.Button(
                                        " Upload XLSX",
                                        color="primary",
                                        className="bi bi-upload",
                                        outline=True,
                                    ),
                                    id="upload_xlsx"
                                ),
                                dbc.Button(
                                    " Adicionar",
                                    color="primary",
                                    className="bi bi-plus-circle",
                                    outline=True,
                                    id="insert_btn"
                                )
                            ], style={"width": "100%"}
                        ),
                        width=12
                    )
                ]
            ),
            html.Br(),
            dbc.Card(
                dbc.Tabs(
                    [
                        dbc.Tab([
                            dcc.Loading([
                                html.Div(id='disco')
                            ]
                            ),
                        ], label="Artistas",
                        ),
                        dbc.Tab(
                            dbc.Col([
                                dcc.Loading(
                                    dcc.Graph(
                                        id='total_year_graph',
                                        responsive=True
                                    )
                                ),
                                html.Div(id="total_year_data")
                            ], width=12
                            ), label="Ano de Lançamento"
                        ),
                        dbc.Tab(
                            dbc.Col([
                                dcc.Loading(
                                    dcc.Graph(
                                        id='total_purchase_graph',
                                        responsive=True
                                    )
                                ),
                                html.Div(id="total_purchase_data")
                            ], width=12
                            ), label="Ano de Aquisição"
                        ),
                    ]
                ),className='dark-tabs'
            )
        ], className='custom-content'
    )

    def callbacks(self):

        @app.callback(
            Output("total_year_graph", 'figure'),
            Output("total_purchase_graph", 'figure'),
            Input('df', 'data'),
            Input('filter_contents', 'data'),
        )
        def render(_, _filter):
            if _filter:
                _query = ""
                for key, value in _filter.items():
                    _query += f"""{key} == "{value}" & """

                _query = _query[:_query.rfind("&")]
                df = self.conn.qyery("CD").query(_query)
            else:
                df = self.conn.qyery("CD")

            df['RELEASE_YEAR'] = pd.to_numeric(
                df['RELEASE_YEAR'], errors='coerce')

            total_year = px.bar(df.groupby(['RELEASE_YEAR'])['RELEASE_YEAR'].count(),
                                labels={
                "index": "Ano",
                "value": "Total"
            },
                title="Ano de Lançamento",
                text_auto=True,
                height=600
            ).update_layout(showlegend=False, clickmode='event+select')
            total_year.update_layout(
                showlegend=False, hovermode="x unified", clickmode='event+select')
            total_year.update_traces(
                hovertemplate='Total: %{y}<extra></extra>')
            try:
                df['PURCHASE'] = pd.to_datetime(
                    df['PURCHASE'], errors='coerce')
                count = df.groupby(df['PURCHASE'].dt.year)['PURCHASE'].count()
            except:
                count = None
            total_purchase = px.bar(
                count,
                labels={
                    "index": "Ano",
                    "value": "Total"
                },
                title="Ano de Aquisição",
                text_auto=True,
                height=600
            ).update_layout(showlegend=False, clickmode='event+select')
            return total_year, total_purchase

        @app.callback(
            Output('total_purchase_data', 'children'),
            Input("total_purchase_graph", 'clickData')
        )
        def display_click_data(clickData):
            if clickData:
                df = self.conn.qyery("CD")
                df['PURCHASE'] = pd.to_datetime(
                    df['PURCHASE'], errors='coerce')
                df = df[df['PURCHASE'].dt.year == clickData['points'][0]['x']]
                table_header = [
                    html.Thead(html.Tr([html.Th("ARTIST"), html.Th("TITLE")]))
                ]
                table_body = [
                    html.Tbody([
                        html.Tr([
                            html.Td(row["ARTIST"]),
                            html.Td(row["TITLE"])
                        ]) for row in df.to_dict('records')
                    ])
                ]
                table = dbc.Table(table_header + table_body, bordered=True)
                return table

        @app.callback(
            Output('total_year_data', 'children'),
            Input("total_year_graph", 'clickData')
        )
        def display_click_data(clickData):
            if clickData:
                df = self.conn.qyery("CD")
                df = df[df['RELEASE_YEAR'] == clickData['points'][0]['x']]
                table_header = [
                    html.Thead(html.Tr([html.Th("ARTIST"), html.Th("TITLE")]))
                ]
                table_body = [
                    html.Tbody([
                        html.Tr([
                            html.Td(row["ARTIST"]),
                            html.Td(row["TITLE"])
                        ]) for row in df.to_dict('records')
                    ])
                ]
                table = dbc.Table(table_header + table_body, bordered=True)
                return table

        @app.callback(
            Output('disco', 'children'),
            Output('filter_contents', 'data'),
            Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
            Input('df', 'data'),
            Input('url', 'pathname'),
            State('filter_contents', 'data'),
            prevent_initial_call=True
        )
        def update_output(value, _, url, _filter):
            cxt = callback_context.triggered
            if not any(value):
                if cxt[0]['value'] == None:
                    try:
                        _filter.pop(
                            loads(cxt[0]['prop_id'].split('.')[0])["index"]
                        )
                    except:
                        pass
                welcome = dbc.Alert(
                    [
                        html.H4("Bem Vindo!", className="alert-heading"),
                        html.P(
                            "Utilize os filtros para realizar a pesquisa"
                        ),
                    ], style={"margin-top": "1rem", "background-color": "#fff", "color": "#0d6efd", "border-color": "#0d6efd"}
                )
                return welcome, _filter
            else:
                if cxt[0]['prop_id'].split('.')[0] not in ["df"]:
                    _filter_index = loads(
                        cxt[0]['prop_id'].split('.')[0])["index"]
                    _filter[_filter_index] = cxt[0]["value"]
                    _filter = dict((k, v)
                                   for k, v in _filter.items() if v is not None)
                _query = ""
                for key, value in _filter.items():
                    _query += f"""{key} == "{value}" & """

                _query = _query[:_query.rfind("&")]
                df = self.conn.qyery("CD")
                if len(df.query(_query)) > 50:
                    warning = dbc.Alert(
                        [
                            html.H4("Acima de 50 unidades encontradas",
                                    className="alert-heading"),
                            html.P(
                                "Utilize o filtro de forma mais granular ou Realize o download da Planilha"
                            ),
                        ], style={"margin-top": "1rem"}
                    )
                    return warning, _filter
                df = df.query(_query).groupby('ARTIST', as_index=False)
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
                                    dbc.Col(
                                        dbc.ListGroup(
                                            [
                                                dbc.ListGroupItem(
                                                    f' ANO DE LANÇAMENTO: {row["RELEASE_YEAR"] if row["RELEASE_YEAR"] is not None else ""}',
                                                    className="bi bi-calendar-event"
                                                ),
                                                dbc.ListGroupItem(
                                                    f' ANO DA EDIÇÃO: {int(row["EDITION_YEAR"]) if row["EDITION_YEAR"] is not None else ""}',
                                                    className="bi bi-calendar-event"
                                                ),
                                                dbc.ListGroupItem(
                                                    f' MEDIA: {row["MEDIA"] if row["MEDIA"] is not None else ""}', className="bi bi-vinyl"
                                                ),
                                                dbc.ListGroupItem(
                                                    f' AQUISIÇÃO: {row["PURCHASE"].strftime("%d/%m/%Y") if row["PURCHASE"] is not None else "" }',
                                                    className="bi bi-cart3"
                                                )
                                            ]
                                        ), width=4),

                                    dbc.Col(
                                        dbc.ListGroup([
                                            dbc.ListGroupItem(
                                                f' ORIGEM: {row["ORIGIN"]  if row["ORIGIN"] is not None else "" }',
                                                className="bi bi-house"
                                            ),
                                            dbc.ListGroupItem(
                                                f' IFPI MASTERING: {row["IFPI_MASTERING"]  if row["IFPI_MASTERING"] is not None else "" }',
                                                className="bi bi-body-text"
                                            ),
                                            dbc.ListGroupItem(
                                                f' IFPI MOULD: {row["IFPI_MOULD"]  if row["IFPI_MOULD"] is not None else "" }',
                                                className="bi bi-body-text"
                                            )
                                        ]), width=4),

                                    dbc.Col(
                                        dbc.ListGroup([
                                            dbc.ListGroupItem(
                                                f' CÓDIGO DE BARRAS: {row["BARCODE"] if row["BARCODE"] is not None else "" }',
                                                className="bi bi-body-text"
                                            ),
                                            dbc.ListGroupItem(
                                                f' MATRIZ: {row["MATRIZ"]  if row["MATRIZ"] is not None else "" }',
                                                className="bi bi-body-text"
                                            ),
                                            dbc.ListGroupItem(
                                                f' LOTE: {row["LOTE"] if row["LOTE"] is not None else "" }',
                                                className="bi bi-body-text"
                                            )
                                        ]), width=4
                                    )
                                ],
                                align="start",
                            ),
                            dbc.Row(
                                dbc.Col(
                                    [dbc.Button(
                                        html.I(className="bi bi-pencil-fill"),
                                        color="warning",
                                        outline=True,
                                        className="me-1",
                                        id={
                                            'type': 'edit_button',
                                            'index': f"{row['_id']}"
                                        },
                                    ), dbc.Button(
                                        html.I(className="bi bi-trash2-fill"),
                                        color="danger",
                                        outline=True,
                                        className="me-1",
                                        id={
                                            'type': 'delete_button',
                                            'index': f"{row['_id']}"
                                        },
                                    )], width=2),
                                justify="end",
                            ),
                            html.Hr(),
                            self.discogs_get_url(row)

                        ], title=f'{int(row["RELEASE_YEAR"]) if row["RELEASE_YEAR"] is not None else ""} - {row["TITLE"]}')
                        for row in group.sort_values("RELEASE_YEAR").to_dict('records')], start_collapsed=True)
                ], title=name,
                ) for name, group in df], start_collapsed=True)
            return accord, _filter

        @ app.callback(
            Output("upload_alert", "children"),
            Input('upload_xlsx', 'contents'),
            State("upload_xlsx", "filename"),
            prevent_initial_call=True,
        )
        def on_button_click(data, filename):
            content_type, content_string = data.split(',')
            decoded = base64.b64decode(content_string)

            if filename is None:
                raise ""
            else:
                if 'csv' in filename:
                    df = pd.read_csv(
                        StringIO(decoded.decode('utf-8')), sep=";")
                elif 'xls' in filename:
                    df = pd.read_excel(
                        BytesIO(decoded), dtype={'BARCODE': str})
                else:
                    return dbc.Alert("FORMATO INVALIDO",
                                     is_open=True,  duration=4000, color="danger")

                COLUMNS = ('RELEASE_YEAR', 'ARTIST', 'TITLE', 'MEDIA', 'PURCHASE', 'ORIGIN',
                           'EDITION_YEAR', 'IFPI_MASTERING', 'IFPI_MOULD', 'BARCODE', 'MATRIZ', 'LOTE')

                for col in df.select_dtypes(include=['datetime64']).columns.tolist():
                    df[col] = df[col].astype(str)

                validate_schema = pa.DataFrameSchema({
                    "RELEASE_YEAR": pa.Column(int),
                    "ARTIST": pa.Column(str),
                    "TITLE": pa.Column(str),
                    "MEDIA": pa.Column(str),
                    "PURCHASE": pa.Column(object, nullable=True),
                    "ORIGIN": pa.Column(str, nullable=True),
                    "EDITION_YEAR": pa.Column(float, nullable=True),
                    "IFPI_MASTERING": pa.Column(str, nullable=True),
                    "IFPI_MOULD": pa.Column(str, nullable=True),
                    "MATRIZ": pa.Column(str, nullable=True),
                    "LOTE": pa.Column(str, nullable=True)
                })

                try:
                    validate_schema(df)
                    df.replace({pd.NaT: None, np.nan: None, "NaT": None,
                                "": None, "None": None}, inplace=True)
                    df = df.to_dict("records")

                    newList = []

                    for d in df:
                        newDf = {}
                        for key, value in d.items():
                            if key in COLUMNS:
                                newDf[key] = value
                        newList.append(newDf)

                    self.conn.drop("CD")
                    self.conn.insert_many("CD", newList)

                    return dbc.Alert("SALVO",
                                     is_open=True,  duration=4000)
                except pa.errors.SchemaError as error:
                    return dbc.Alert([
                        html.P(
                            f"ERRO NOS DADOS DA COLUNA: {error.schema.name}"),
                        html.P(f"TIPO ESPERADO: {error.check}")
                    ], is_open=True, color="danger"
                    )

        @app.callback(
            Output("download_xlsx", "data"),
            Input("download_xlsx_btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def on_button_click(n):
            if n is None:
                raise ""
            else:
                df = self.conn.qyery("CD")
                df.drop('_id', axis=1, inplace=True)
                df.drop('DISCOGS', axis=1, inplace=True)
                df['PURCHASE'] = pd.to_datetime(df['PURCHASE']).dt.date
                df.replace({pd.NaT: None, np.nan: None, "NaT": None,
                           "": None, "None": None}, inplace=True)
                return dcc.send_data_frame(df.to_excel, "collection.xlsx")
