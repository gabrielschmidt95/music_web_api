import base64
from io import BytesIO, StringIO
from json import loads
from os import environ

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import pandera as pa
import plotly.express as px
import requests
import spotipy
from dash import ALL, Input, Output, State, callback_context, dcc, html
from spotipy.oauth2 import SpotifyClientCredentials

from server import app
import flask


class Content:
    def __init__(self):
        self.MAX_INDEX = 3
        self.discogs_url = "https://api.discogs.com/database/search"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + environ["DB_TOKEN"],
        }

    def get_album_for_artist(self, artist, album):
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        results = sp.search(q="artist:" + artist + " album:" + album, type="album")
        if results:
            items = results["albums"]["items"]
            if len(items) > 0:
                return items
            else:
                return None
        else:
            return None

    def discogs_get_url(self, row):
        if (
            "discogs" not in row
            or row["discogs"] is None
            or "tracks" not in row["discogs"]
        ):
            params = {
                "token": environ["DISCOGS_TOKEN"],
                "artist": row["artist"].lower() if not None else "",
                "release_title": row["title"].lower()
                if row["title"].lower() is not None
                else "",
                "barcode": str(row["barcode"])
                if row["barcode"] is not None and row["barcode"] != "None"
                else "",
                "country": row["origin"].lower()
                if not None and row["origin"].lower() != "none"
                else "",
                "year": str(row["releaseYear"]) if not None else "",
                "format": "album",
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
                            resp = requests.get(self.discogs_url, params=params)
                            result = resp.json()["results"]
                            if len(result) == 0:
                                params.pop("barcode")
                                resp = requests.get(self.discogs_url, params=params)
                                result = resp.json()["results"]

                if len(result) > 0:
                    row["DISCOGS"] = result[0]
                    row["DISCOGS"]["urls"] = [
                        {"id": r["id"], "uri": r["uri"]} for r in result
                    ]
                    row["DISCOGS"]["len"] = len(result)
                    _id = row["DISCOGS"]["id"]
                    _type = row["DISCOGS"]["type"]
                    tracks = requests.get(f"https://api.discogs.com/{_type}s/{_id}")
                    if tracks.status_code == 200:
                        row["DISCOGS"].update(tracks=tracks.json()["tracklist"])

                    # self.conn.replace_one("CD", row["_id"], row)
                else:
                    return html.Div("Nao encontrado no Discogs")
            else:
                return html.Div(f"Error:{resp.status_code}")

        if "tracks" in row["discogs"] and row["discogs"]["tracks"]:
            tracklist = row["discogs"]["tracks"]
        else:
            tracklist = []

        if "spotify" in row and row["spotify"]["name"]:
            spotify = dbc.Button(
                f' SPOTIFY - {row["spotify"]["name"]}',
                href=row["spotify"]["external_urls"]["spotify"],
                className="bi bi-music-note-beamed",
                external_link=True,
                target="_blank",
                style={"margin-bottom": "1rem"},
                color="success",
            )
        else:
            print("Getting Spotify")
            # spotify_get = self.get_album_for_artist(row["artist"], row["title"])
            # if spotify_get:
            #     row["SPOTIFY"] = spotify_get[0]
            #     # self.conn.replace_one("CD", row["_id"], row)
            #     spotify = dbc.Button(
            #         f' SPOTIFY - {row["SPOTIFY"]["name"]}',
            #         href=row["SPOTIFY"]["external_urls"]["spotify"],
            #         className="bi bi-music-note-beamed",
            #         external_link=True,
            #         target="_blank",
            #         style={"margin-bottom": "1rem"},
            #         color="success",
            #     )
            # else:
            spotify = html.Div()

        if not row["discogs"]["urls"]:
            row["discogs"]["urls"] = []

        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            html.Img(src=row["discogs"]["cover_image"]),
                            justify="center",
                        )
                    ],
                    width=4,
                    align="center",
                ),
                dbc.Col(
                    [
                        spotify,
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        dbc.ListGroup(
                                            [
                                                dbc.ListGroupItem(
                                                    dbc.CardLink(
                                                        f'DISCOGS - {url["id"]}',
                                                        href=f"https://www.discogs.com{url['uri'] if 'uri' in url else ''}",
                                                        className="bi bi-body-text",
                                                        external_link=True,
                                                        target="_blank",
                                                    )
                                                )
                                                for url in row["discogs"]["urls"]
                                            ]
                                        ),
                                    ],
                                    title=f"ARTIGOS ENCONTRADOS: {row['discogs']['len'] if 'len' in row['discogs'] else 0}",
                                ),
                            ],
                            start_collapsed=True,
                        ),
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        dbc.ListGroup(
                                            [
                                                dbc.ListGroupItem(
                                                    f'{t["position"]} - {t["title"]}'
                                                )
                                                for t in tracklist
                                            ]
                                        )
                                    ],
                                    title="Lista de Faixas",
                                ),
                            ],
                            start_collapsed=True,
                        ),
                    ],
                    width=8,
                ),
            ]
        )

    def layout(self):
        print("Content Layout")
        return html.Div(
            [
                dcc.Download(id="download_xlsx"),
                html.Div(id="download_alert"),
                html.Div(id="upload_alert"),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        " Download XLSX",
                                        color="primary",
                                        className="bi bi-download",
                                        outline=True,
                                        id="download_xlsx_btn",
                                    ),
                                    dcc.Upload(
                                        dbc.Button(
                                            " Upload XLSX",
                                            color="primary",
                                            className="bi bi-upload",
                                            outline=True,
                                        ),
                                        id="upload_xlsx",
                                    ),
                                    dbc.Button(
                                        " Adicionar",
                                        color="primary",
                                        className="bi bi-plus-circle",
                                        outline=True,
                                        id="insert_btn",
                                    ),
                                    dbc.Label(
                                        style={
                                            "margin-top": "0.5rem",
                                            "margin-left": "2rem",
                                        },
                                        id="user_label",
                                    ),
                                ],
                                style={"width": "100%"},
                            ),
                            width=12,
                        )
                    ]
                ),
                html.Br(),
                dbc.Card(
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                [
                                    dcc.Loading([html.Div(id="disco")]),
                                ],
                                label="Artistas",
                            ),
                            dbc.Tab(
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            dcc.Graph(
                                                id="total_year_graph", responsive=True
                                            )
                                        ),
                                        html.Div(id="total_year_data"),
                                    ],
                                    width=12,
                                ),
                                label="Ano de Lançamento",
                            ),
                            dbc.Tab(
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            dcc.Graph(
                                                id="total_purchase_graph",
                                                responsive=True,
                                            )
                                        ),
                                        html.Div(id="total_purchase_data"),
                                    ],
                                    width=12,
                                ),
                                label="Ano de Aquisição",
                            ),
                        ]
                    )
                ),
            ],
            className="custom-content",
        )

    def callbacks(self):
        @app.callback(
            Output("total_year_graph", "figure"),
            Output("total_purchase_graph", "figure"),
            Input("df", "data"),
            Input("filter_contents", "data"),
        )
        def render(_, _filter):
            totals_by_year = requests.get(
                environ["DB_API"] + "totals", headers=self.headers
            ).json()
            df = pd.DataFrame().from_dict(
                totals_by_year["year"], orient="index", columns=["TOTAL"]
            )

            total_year = px.bar(
                df,
                x=df.index,
                y="TOTAL",
                labels={"index": "Ano", "value": "Total"},
                title="Ano de Lançamento",
                text_auto=True,
                height=600,
            ).update_layout(showlegend=False, clickmode="event+select")
            total_year.update_layout(
                showlegend=False, hovermode="x unified", clickmode="event+select"
            )
            total_year.update_traces(hovertemplate="Total: %{y}<extra></extra>")

            # Purchase
            df_p = pd.DataFrame().from_dict(
                totals_by_year["buy"], orient="index", columns=["TOTAL"]
            )

            total_purchase = px.bar(
                df_p,
                x=df_p.index,
                y="TOTAL",
                labels={"index": "Ano", "value": "Total"},
                title="Ano de Aquisição",
                text_auto=True,
                height=600,
            ).update_layout(showlegend=False, clickmode="event+select")
            return total_year, total_purchase

        @app.callback(
            Output("total_purchase_data", "children"),
            Input("total_purchase_graph", "clickData"),
        )
        def display_click_data(clickData):
            if clickData:
                year_selected = requests.post(
                    environ["DB_API"] + "album/year/",
                    headers=self.headers,
                    json={
                        "year": int(clickData["points"][0]["x"]),
                        "metric": "purchase"
                    },
                ).json()
                df = pd.DataFrame().from_dict(year_selected)
                table_header = [
                    html.Thead(html.Tr([html.Th("ARTIST"), html.Th("TITLE"),html.Th("COMPRA")]))
                ]
                table_body = [
                    html.Tbody(
                        [
                            html.Tr([html.Td(row["artist"]), html.Td(row["title"]),html.Td(row["purchase"])])
                            for row in df.to_dict("records")
                        ]
                    )
                ]
                table = dbc.Table(table_header + table_body, bordered=True)
                return table

        @app.callback(
            Output("total_year_data", "children"),
            Input("total_year_graph", "clickData"),
        )
        def display_click_data(clickData):
            if clickData:
                year_selected = requests.post(
                    environ["DB_API"] + "album/year/",
                    headers=self.headers,
                    json={
                        "year": int(clickData["points"][0]["x"]),
                        "metric": "release_year"
                    },
                ).json()
                df = pd.DataFrame().from_dict(year_selected)
                table_header = [
                    html.Thead(html.Tr([html.Th("ARTIST"), html.Th("TITLE"),html.Th("MEDIA")]))
                ]
                table_body = [
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(row["artist"]),
                                    html.Td(row["title"]),
                                    html.Td(row["media"]),
                                ]
                            )
                            for row in df.to_dict("records")
                        ]
                    )
                ]
                table = dbc.Table(table_header + table_body, bordered=True)
                return table

        @app.callback(
            Output("disco", "children"),
            Output("filter_contents", "data"),
            Output("user_label", "children"),
            Input({"type": "filter-dropdown", "index": ALL}, "value"),
            Input("df", "data"),
            Input("url", "pathname"),
            State("filter_contents", "data"),
            prevent_initial_call=True,
        )
        def update_output(value, _, url, _filter, request=flask.request):
            if "AUTH-USER" in request.cookies and "AUTH-USER-IMAGE" in request.cookies:
                user = [
                    html.Img(
                        src=request.cookies["AUTH-USER-IMAGE"],
                        width="30px",
                        style={"border-radius": "50%"},
                    ),
                    f' {request.cookies["AUTH-USER"]}',
                ]
            else:
                user = " No User"

            cxt = callback_context.triggered
            if not any(value):
                print("No Value")
                if cxt[0]["value"] == None:
                    try:
                        _filter = {}
                    except Exception:
                        pass
                welcome = dbc.Alert(
                    [
                        html.H4("Bem Vindo!", className="alert-heading"),
                        html.P("Utilize os filtros para realizar a pesquisa"),
                    ],
                    style={
                        "margin-top": "1rem",
                        "background-color": "#fff",
                        "color": "#0d6efd",
                        "border-color": "#0d6efd",
                    },
                )
                return welcome, _filter, user
            else:
                if cxt[0]["prop_id"].split(".")[0] not in ["df"]:
                    _filter_index = loads(cxt[0]["prop_id"].split(".")[0])["index"]
                    _filter[_filter_index] = cxt[0]["value"]
                    _filter = dict((k, v) for k, v in _filter.items() if v is not None)
                artist = requests.post(
                    environ["DB_API"] + "albuns",
                    headers=self.headers,
                    json={
                        "artist": _filter["ARTIST"] if "ARTIST" in _filter else "",
                        "media": _filter["MEDIA"] if "MEDIA" in _filter else "",
                        "origin": _filter["ORIGIN"] if "ORIGIN" in _filter else "",
                    },
                ).json()
                if not artist:
                    warning = dbc.Alert(
                        [
                            html.H4(
                                "Nenhum resultado encontrado", className="alert-heading"
                            ),
                            html.P("Utilize os filtros para realizar a pesquisa"),
                        ],
                        style={
                            "margin-top": "1rem",
                            "background-color": "#fff",
                            "color": "#0d6efd",
                            "border-color": "#0d6efd",
                        },
                    )
                    return warning, _filter, user

                df = pd.DataFrame.from_dict(artist)
                df = df.sort_values("releaseYear").to_dict("records")

                n_dct = {}
                for v in df:
                    if v["artist"] not in n_dct:
                        n_dct[v["artist"]]  = []
                    n_dct[v["artist"]].append(v)

                if len(df) > 50:
                    warning = dbc.Alert(
                        [
                            html.H4(
                                "Acima de 50 unidades encontradas",
                                className="alert-heading",
                            ),
                            html.P(
                                "Utilize o filtro de forma mais granular ou Realize o download da Planilha"
                            ),
                        ],
                        style={"margin-top": "1rem"},
                    )
                    return warning, _filter, user
            accord = dbc.Accordion(
                [dbc.AccordionItem(
                    [
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        html.H4(
                                            f' {row["title"]}',
                                            className="card-title bi bi-book",
                                        ),
                                        html.H5(
                                            f' {row["artist"]}',
                                            className="card-title bi bi-person",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                f' ANO DE LANÇAMENTO: {row["releaseYear"] if row["releaseYear"] is not None else ""}',
                                                                className="bi bi-calendar-event",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' ANO DA EDIÇÃO: {int(row["editionYear"]) if row["editionYear"] is not None else ""}',
                                                                className="bi bi-calendar-event",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' MEDIA: {row["media"] if row["media"] is not None else ""}',
                                                                className="bi bi-vinyl",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' AQUISIÇÃO: {row["purchase"] if row["purchase"] is not None else "" }',
                                                                className="bi bi-cart3",
                                                            ),
                                                        ]
                                                    ),
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                f' ORIGEM: {row["origin"]  if row["origin"] is not None else "" }',
                                                                className="bi bi-house",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' IFPI MASTERING: {row["ifpiMastering"]  if row["ifpiMastering"] is not None else "" }',
                                                                className="bi bi-body-text",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' IFPI MOULD: {row["ifpiMould"]  if row["ifpiMould"] is not None else "" }',
                                                                className="bi bi-body-text",
                                                            ),
                                                        ]
                                                    ),
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                f' CÓDIGO DE BARRAS: {row["barcode"] if row["barcode"] is not None else "" }',
                                                                className="bi bi-body-text",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' MATRIZ: {row["matriz"]  if row["matriz"] is not None else "" }',
                                                                className="bi bi-body-text",
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' LOTE: {row["lote"] if row["lote"] is not None else "" }',
                                                                className="bi bi-body-text",
                                                            ),
                                                        ]
                                                    ),
                                                    width=4,
                                                ),
                                            ],
                                            align="start",
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        html.I(
                                                            className="bi bi-pencil-fill"
                                                        ),
                                                        color="warning",
                                                        outline=True,
                                                        className="me-1",
                                                        id={
                                                            "type": "edit_button",
                                                            "index": f"{row['id']}",
                                                        },
                                                    ),
                                                    dbc.Button(
                                                        html.I(
                                                            className="bi bi-trash2-fill"
                                                        ),
                                                        color="danger",
                                                        outline=True,
                                                        className="me-1",
                                                        id={
                                                            "type": "delete_button",
                                                            "index": f"{row['id']}",
                                                        },
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                            justify="end",
                                        ),
                                        html.Hr(),
                                        self.discogs_get_url(row),
                                    ],
                                    title=f'{int(row["releaseYear"]) if row["releaseYear"] is not None else ""} - {row["title"]}',
                                )
                                for row in value
                            ],
                            start_collapsed=True,
                        )
                    ],
                    title=key,
                ) for key,value in n_dct.items()],
                start_collapsed=True,
            )
            return accord, _filter, user

        @app.callback(
            Output("upload_alert", "children"),
            Input("upload_xlsx", "contents"),
            State("upload_xlsx", "filename"),
            prevent_initial_call=True,
        )
        def on_button_click(data, filename):
            content_type, content_string = data.split(",")
            decoded = base64.b64decode(content_string)

            if filename is None:
                raise ""
            else:
                if "csv" in filename:
                    df = pd.read_csv(StringIO(decoded.decode("utf-8")), sep=";")
                elif "xls" in filename:
                    df = pd.read_excel(BytesIO(decoded), dtype={"BARCODE": str})
                else:
                    return dbc.Alert(
                        "FORMATO INVALIDO", is_open=True, duration=4000, color="danger"
                    )

                COLUMNS = (
                    "RELEASE_YEAR",
                    "ARTIST",
                    "TITLE",
                    "MEDIA",
                    "PURCHASE",
                    "ORIGIN",
                    "EDITION_YEAR",
                    "IFPI_MASTERING",
                    "IFPI_MOULD",
                    "BARCODE",
                    "MATRIZ",
                    "LOTE",
                )

                for col in df.select_dtypes(include=["datetime64"]).columns.tolist():
                    df[col] = df[col].astype(str)

                validate_schema = pa.DataFrameSchema(
                    {
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
                        "LOTE": pa.Column(str, nullable=True),
                    }
                )

                try:
                    validate_schema(df)
                    df.replace(
                        {
                            pd.NaT: None,
                            np.nan: None,
                            "NaT": None,
                            "": None,
                            "None": None,
                        },
                        inplace=True,
                    )
                    df = df.to_dict("records")

                    newList = []

                    for d in df:
                        newDf = {}
                        for key, value in d.items():
                            if key in COLUMNS:
                                newDf[key] = value
                        newList.append(newDf)

                    # self.conn.drop("CD")
                    # self.conn.insert_many("CD", newList)

                    return dbc.Alert("SALVO", is_open=True, duration=4000)
                except pa.errors.SchemaError as error:
                    return dbc.Alert(
                        [
                            html.P(f"ERRO NOS DADOS DA COLUNA: {error.schema.name}"),
                            html.P(f"TIPO ESPERADO: {error.check}"),
                        ],
                        is_open=True,
                        color="danger",
                    )

        @app.callback(
            Output("download_xlsx", "data"),
            Input("download_xlsx_btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def on_button_click(n):
            if n is None:
                raise ValueError()
            else:
                all_data = requests.get(
                environ["DB_API"] + "all", headers=self.headers
                ).json()
                df = pd.DataFrame().from_dict(all_data)
                df = df.drop("id", axis=1)
                df = df.drop("discogs", axis=1)
                df = df.drop("spotify", axis=1)
                df["purchase"] = pd.to_datetime(df["purchase"]).dt.date
                df.replace(
                    {pd.NaT: None, np.nan: None, "NaT": None, "": None, "None": None},
                    inplace=True,
                )
                return dcc.send_data_frame(df.to_excel, "collection.xlsx")
