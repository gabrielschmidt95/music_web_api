from json import loads
from datetime import datetime
from typing import Union, Any

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import pandera as pa
import plotly.express as px
import spotipy
from dash import ALL, Input, Output, State, callback_context, dcc, html, no_update

from spotipy.oauth2 import SpotifyClientCredentials
from api.db_api import DBApi
from api.discogs import try_get_discogs, get_params, get_tracks, get_discogs

from server import app
import flask

CLICK_MODE = "event+select"
BI_TEXT = "bi bi-body-text"
BI_CALENDAR = "bi bi-calendar-event"
UPDATE_ENDPOINT = "update/album"
ERRO_DADOS = "Erro ao carregar dados"


class Content:
    def __init__(self) -> None:
        self.MAX_INDEX = 3
        self.api = DBApi()

    def get_album_for_artist(self, artist, album) -> list:
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        results = sp.search(q="artist:" + artist + " album:" + album, type="album")
        if results:
            items = results["albums"]["items"]
            if len(items) > 0:
                return items
            else:
                return []
        else:
            return []

    def get_spotify(self, row) -> Union[html.Div, dbc.Button]:
        if row["spotify"]["name"] == "NOT_FOUND":
            spotify = html.Div("Nao encontrado no Spotify")
        elif "spotify" in row and row["spotify"]["name"]:
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
            spotify_get = self.get_album_for_artist(row["artist"], row["title"])
            if spotify_get:
                row["spotify"] = spotify_get[0]

                self.api.post(UPDATE_ENDPOINT, row)

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
                row["spotify"] = {"name": "NOT_FOUND"}

                self.api.post(UPDATE_ENDPOINT, row)
                spotify = html.Div("Nao encontrado no Spotify")

        return spotify

    def get_image(self, cover_image) -> dbc.Col:
        return dbc.Col(
            [
                dbc.Row(
                    html.Img(src=cover_image),
                    justify="center",
                )
            ],
            width=4,
            align="center",
        )

    def return_no_discogs(self, row) -> dbc.Row:
        # load cover image from assets
        cover_image = "/assets/no_image_available.png"
        return dbc.Row(
            [
                self.get_image(cover_image),
                dbc.Col(
                    [
                        self.get_spotify(row),
                        html.Div("Nao encontrado no Discogs"),
                        dbc.Button(
                            "Fix Discogs?",
                            color="warning",
                            outline=True,
                            className="me-1",
                            id={
                                "type": "fix_discogs",
                                "index": f"{row['id']}",
                            },
                        ),
                    ],
                    width=4,
                    align="center",
                ),
            ]
        )

    def get_tracklist(self, row) -> list:
        if "tracks" in row["discogs"] and row["discogs"]["tracks"]:
            tracklist = row["discogs"]["tracks"]
        else:
            tracklist = []

        return tracklist

    def discogs_get_url(self, row) -> dbc.Row:
        if "discogs" not in row or row["discogs"] is None or row["discogs"]["id"] == 0:
            if row["discogs"]["type"] == "NOT_FOUND":
                return self.return_no_discogs(row)

            params = get_params(row)

            resp = get_discogs(row)

            if resp:
                result = resp.json()
                if "results" not in result:
                    return self.return_no_discogs(row)

                result = result["results"]

                if len(result) == 0:
                    result = try_get_discogs(params)

                if len(result) == 0:
                    row["discogs"] = {"type": "NOT_FOUND"}
                    self.api.post(UPDATE_ENDPOINT, row)
                    return self.return_no_discogs(row)

                row["discogs"] = result[0]
                row["discogs"]["urls"] = [
                    {"id": r["id"], "uri": r["uri"]} for r in result
                ]
                row["discogs"]["len"] = len(result)
                _id = row["discogs"]["id"]
                _type = row["discogs"]["type"]
                tracks = get_tracks(_type, _id)
                if tracks:
                    row["discogs"].update(tracks=tracks)

                result = self.api.post(UPDATE_ENDPOINT, row)

                print("ID", result)

            else:
                return dbc.Row(html.Div(f"Error on get Discogs for {row['title']}"))

        if not row["discogs"]["urls"]:
            row["discogs"]["urls"] = []

        spotify = self.get_spotify(row)

        return dbc.Row(
            [
                self.get_image(
                    row["discogs"]["cover_image"]
                    if row["discogs"]["cover_image"]
                    else "/assets/no_image_available.png"
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
                                                        className=BI_TEXT,
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
                                                for t in self.get_tracklist(row)
                                            ]
                                        )
                                    ],
                                    title="Lista de Faixas",
                                ),
                            ],
                            start_collapsed=True,
                        ),
                        dbc.Button(
                            "Fix Discogs?",
                            color="warning",
                            outline=True,
                            className="me-1",
                            id={
                                "type": "fix_discogs",
                                "index": f"{row['id']}",
                            },
                        ),
                    ],
                    width=8,
                ),
            ]
        )

    def button_group(self) -> dbc.ButtonGroup:
        return dbc.ButtonGroup(
            [
                dbc.Button(
                    " Download XLSX",
                    color="primary",
                    className="bi bi-download",
                    outline=True,
                    id="download_xlsx_btn",
                ),
                dbc.Button(
                    " Adicionar",
                    color="primary",
                    className="bi bi-plus-circle",
                    outline=True,
                    id="insert_btn",
                ),
                html.Div(
                    dbc.Label(
                        style={
                            "margin-top": "0.5rem",
                            "margin-left": "2rem",
                        },
                        id="user_label",
                    ),
                    style={
                        "border-color": "#fff",
                        "border-width": "1px",
                        "border-style": "solid",
                        "border-radius": "5px",
                    },
                ),
            ],
            style={"width": "100%"},
        )

    def layout(self) -> html.Div:
        return html.Div(
            [
                dcc.Download(id="download_xlsx"),
                html.Div(id="download_alert"),
                html.Div(id="upload_alert"),
                dbc.Row(
                    [
                        dbc.Col(
                            self.button_group(),
                            width=12,
                        )
                    ],
                    style={
                        "position": "sticky",
                        "top": "0",
                        "z-index": "1",
                        "background-color": "#fff",
                    },
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
                            dbc.Tab(
                                [
                                    dcc.Loading(
                                        [html.Div(id="no_discogs")],
                                        id="no_discogs_loading",
                                    ),
                                ],
                                label="Sem Discogs",
                                id="no_discogs_tab",
                            ),
                        ]
                    )
                ),
            ],
            className="custom-content",
        )

    def callbacks(self) -> None:
        @app.callback(
            Output("total_year_graph", "figure"),
            Output("total_purchase_graph", "figure"),
            Input("df", "data"),
        )
        def render(_) -> Union[html.Div, Any]:
            totals_by_year = self.api.get("totals")
            if "year" not in totals_by_year:
                return (None, None)

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
            ).update_layout(showlegend=False, clickmode=CLICK_MODE)
            total_year.update_layout(
                showlegend=False, hovermode="x unified", clickmode=CLICK_MODE
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
            ).update_layout(showlegend=False, clickmode=CLICK_MODE)
            return total_year, total_purchase

        @app.callback(
            Output("total_purchase_data", "children"),
            Input("total_purchase_graph", "clickData"),
        )
        def __total_purchase__(click_data) -> Union[html.Div, Any]:
            if click_data:
                year_selected = self.api.post(
                    "album/year",
                    {
                        "year": int(click_data["points"][0]["x"]),
                        "metric": "purchase",
                    },
                )
                if not isinstance(year_selected, dict):
                    return dbc.Alert(ERRO_DADOS, color="danger", className="mt-3")

                df = pd.DataFrame().from_dict(year_selected)
                table_header = [
                    html.Thead(
                        html.Th(
                            click_data["points"][0]["x"],
                            colSpan="3",
                            className="table-active",
                            style={"text-align": "center", "font-size": "1.5rem"},
                        )
                    ),
                    html.Thead(
                        html.Tr(
                            [html.Th("ARTIST"), html.Th("TITLE"), html.Th("COMPRA")]
                        )
                    ),
                ]
                table_body = [
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(row["artist"] if row["artist"] else ""),
                                    html.Td(row["title"] if row["title"] else ""),
                                    html.Td(row["purchase"] if row["purchase"] else ""),
                                ]
                            )
                            for row in df.to_dict("records")
                        ]
                    )
                ]
                return dbc.Table(table_header + table_body, bordered=True)

            return no_update

        @app.callback(
            Output("total_year_data", "children"),
            Input("total_year_graph", "clickData"),
        )
        def __total_year_data__(click_data) -> Union[html.Div, Any]:
            if click_data:
                year_selected = self.api.post(
                    "album/year",
                    {
                        "year": int(click_data["points"][0]["x"]),
                        "metric": "release_year",
                    },
                )
                if not isinstance(year_selected, dict):
                    return dbc.Alert(ERRO_DADOS, color="danger", className="mt-3")

                df = pd.DataFrame().from_dict(year_selected)
                table_header = [
                    html.Thead(
                        html.Th(
                            click_data["points"][0]["x"],
                            colSpan="3",
                            className="table-active",
                            style={"text-align": "center", "font-size": "1.5rem"},
                        )
                    ),
                    html.Thead(
                        html.Tr([html.Th("ARTIST"), html.Th("TITLE"), html.Th("MEDIA")])
                    ),
                ]
                table_body = [
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(row["artist"] if row["artist"] else ""),
                                    html.Td(row["title"] if row["title"] else ""),
                                    html.Td(row["media"] if row["media"] else ""),
                                ]
                            )
                            for row in df.to_dict("records")
                        ]
                    )
                ]
                table = dbc.Table(table_header + table_body, bordered=True)
                return table
            
            return no_update

        @app.callback(
            Output("disco", "children"),
            Output("user_label", "children"),
            Output("filter_contents", "data"),
            Input("discogs_id", "data"),
            Input({"type": "filter-dropdown", "index": ALL}, "value"),
            Input("df", "data"),
            Input("url", "pathname"),
            State("filter_contents", "data"),
            prevent_initial_call=True,
        )
        def __update_disco__(
            fix_value, value, _, url, filter_contents, request=flask.request
        )-> Union[html.Div, Any]:
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

            if fix_value and fix_value != "Changed":
                return no_update, no_update, no_update

            if not any(value):
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
                return welcome, user, filter_contents

            artist = []

            if cxt[0]["prop_id"].split(".")[0] not in ["df"]:
                artist_filter = (
                    filter_contents["artist"] if "artist" in filter_contents else ""
                )
                media = filter_contents["media"] if "media" in filter_contents else ""
                origin = (
                    filter_contents["origin"] if "origin" in filter_contents else ""
                )

                try:
                    _filter = loads(cxt[0]["prop_id"].split(".")[0])["index"]

                    filter_contents = {
                        "artist": value[0] if "ARTIST" in _filter else artist_filter,
                        "media": value[1] if "MEDIA" in _filter else media,
                        "origin": value[2] if "ORIGIN" in _filter else origin,
                    }

                except Exception:
                    pass

                artist = self.api.post(
                    "albuns",
                    filter_contents,
                )

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
                return warning, user, filter_contents

            if (
                isinstance(artist, dict)
                and "id" not in artist
                or isinstance(artist, list)
                and "id" not in artist[0]
            ):
                return (
                    dbc.Alert(ERRO_DADOS, color="danger", className="mt-3"),
                    user,
                )

            df = pd.DataFrame.from_dict(artist) # type: ignore
            df = df.sort_values("releaseYear").to_dict("records")

            n_dct = {}
            for v in df:
                if v["artist"] not in n_dct:
                    n_dct[v["artist"]] = []
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
                return warning, user, filter_contents

            accord = dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Accordion(
                                [
                                    dbc.AccordionItem(
                                        [
                                            html.H4(
                                                f' {row["title"] if row["title"] is not None else ""}',
                                                className="card-title bi bi-book",
                                            ),
                                            html.H5(
                                                f' {row["artist"] if row["artist"] is not None else ""}',
                                                className="card-title bi bi-person",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.ListGroup(
                                                            [
                                                                dbc.ListGroupItem(
                                                                    f' ANO DE LANÇAMENTO: {row["releaseYear"] if row["releaseYear"] is not None else ""}',
                                                                    className=BI_CALENDAR,
                                                                ),
                                                                dbc.ListGroupItem(
                                                                    f' ANO DA EDIÇÃO: {int(row["editionYear"]) if row["editionYear"] is not None else ""}',
                                                                    className=BI_CALENDAR,
                                                                ),
                                                                dbc.ListGroupItem(
                                                                    f' MEDIA: {row["media"] if row["media"] is not None else ""}',
                                                                    className="bi bi-vinyl",
                                                                ),
                                                                dbc.ListGroupItem(
                                                                    f' AQUISIÇÃO: {datetime.strptime(row["purchase"],"%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m/%Y") if row["purchase"] else "" }',
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
                                                                    className=BI_TEXT,
                                                                ),
                                                                dbc.ListGroupItem(
                                                                    f' IFPI MOULD: {row["ifpiMould"]  if row["ifpiMould"] is not None else "" }',
                                                                    className=BI_TEXT,
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
                                                                    className=BI_TEXT,
                                                                ),
                                                                dbc.ListGroupItem(
                                                                    f' MATRIZ: {row["matriz"]  if row["matriz"] is not None else "" }',
                                                                    className=BI_TEXT,
                                                                ),
                                                                dbc.ListGroupItem(
                                                                    f' LOTE: {row["lote"] if row["lote"] is not None else "" }',
                                                                    className=BI_TEXT,
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
                                        title=f'{int(row["releaseYear"]) if row["releaseYear"] is not None else ""} - {row["title"] if row["title"] is not None else ""}',
                                    )
                                    for row in value
                                ],
                                start_collapsed=True,
                            )
                        ],
                        title=key,
                    )
                    for key, value in n_dct.items()
                ],
                start_collapsed=True,
            )
            return accord, user, filter_contents

        @app.callback(
            Output("download_xlsx", "data"),
            Input("download_xlsx_btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def __download_xlsx__(n) -> Union[html.Div, Any]:
            if n is None:
                raise ValueError()
            else:
                all_data = self.api.get("all")

                df = pd.DataFrame().from_dict(all_data)
                df = df.drop("id", axis=1)
                df = df.drop("discogs", axis=1)
                df = df.drop("spotify", axis=1)
                df["purchase"] = pd.to_datetime(df["purchase"]).dt.date
                df.replace(
                    {pd.NaT: None, np.nan: None, "NaT": None, "": None, "None": None},  # type: ignore
                    inplace=True,
                )
                return dcc.send_data_frame(df.to_excel, "collection.xlsx")

        @app.callback(
            Output("no_discogs", "children"),
            Input("edit-btn", "n_clicks"),
            Input("discogs_id", "data"),
        )
        def __gen_no_discogs__(_, data)-> Union[html.Div, Any]:
            n_dct = self.api.post("query", {"DISCOGS": {"type": "NOT_FOUND"}})
            if "error" in n_dct:
                return dbc.Alert(ERRO_DADOS, color="danger", className="mt-3")
            return dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Accordion(
                                dbc.AccordionItem(
                                    [
                                        html.H4(
                                            f' {row["title"] if "title" in row else ""}',
                                            className="card-title bi bi-book",
                                        ),
                                        html.H5(
                                            f' {row["artist"] if "artist" in row else ""}',
                                            className="card-title bi bi-person",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                f' ANO DE LANÇAMENTO: {row["releaseYear"] if row["releaseYear"] is not None else ""}',
                                                                className=BI_CALENDAR,
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' ANO DA EDIÇÃO: {int(row["editionYear"]) if row["editionYear"] is not None else ""}',
                                                                className=BI_CALENDAR,
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
                                                                className=BI_TEXT,
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' IFPI MOULD: {row["ifpiMould"]  if row["ifpiMould"] is not None else "" }',
                                                                className=BI_TEXT,
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
                                                                className=BI_TEXT,
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' MATRIZ: {row["matriz"]  if row["matriz"] is not None else "" }',
                                                                className=BI_TEXT,
                                                            ),
                                                            dbc.ListGroupItem(
                                                                f' LOTE: {row["lote"] if row["lote"] is not None else "" }',
                                                                className=BI_TEXT,
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
                                    title=f'{int(row["releaseYear"]) if row["releaseYear"] is not None else ""} - {row["title"] if row["title"] is not None else ""}',
                                ),
                                start_collapsed=True,
                            )
                        ],
                        title=row["title"] if row["title"] is not None else "",
                    )
                    for row in n_dct
                ],
                start_collapsed=True,
            )
