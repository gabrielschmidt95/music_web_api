from datetime import date, datetime
from json import loads
import requests
from os import environ

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback_context, dcc, html, no_update

from server import app


class DataModal:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + environ["OAUTH_TOKEN"],
        }
        self.medias = requests.get(
            environ["DB_API"] + "medias", headers=self.headers
        ).json()
        self.artists = requests.get(
            environ["DB_API"] + "artists", headers=self.headers
        ).json()

    def layout(self):
        return dbc.Col(
            [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="modal_edit_title")),
                        dbc.ModalBody(id="modal_edit_body"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Salvar", id="edit-btn", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    is_open=False,
                    id="modal_edit",
                    size="lg",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Deseja Apagar?")),
                        dbc.ModalBody(id="modal_delete_body"),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Confirma",
                                    id="confirma_btn",
                                    className="ms-auto",
                                    n_clicks=0,
                                ),
                                dbc.Button(
                                    "Cancela",
                                    id="cancela_btn",
                                    className="ms-auto",
                                    n_clicks=0,
                                ),
                            ]
                        ),
                    ],
                    is_open=False,
                    id="modal_delete",
                ),
            ]
        )

    def callbacks(self):
        @app.callback(
            Output("modal_edit_title", "children"),
            Output("modal_edit_body", "children"),
            Output("modal_edit", "is_open"),
            Output("edit_id", "data"),
            Input("edit-btn", "n_clicks"),
            Input("insert_btn", "n_clicks"),
            Input({"type": "edit_button", "index": ALL}, "n_clicks"),
            prevent_initial_call=True,
        )
        def fill_edit_modal(edit_btn, insert_btn, value):
            cxt = callback_context.triggered
            if cxt[0]["prop_id"] == "edit-btn.n_clicks":
                return "", "", False, None
            if cxt[0]["value"]:
                try:
                    _id = loads(cxt[0]["prop_id"].split(".")[0])["index"]
                    media = requests.post(
                        environ["DB_API"] + "album/id",
                        headers=self.headers,
                        json={
                            "id": _id,
                        },
                    ).json()

                except Exception:
                    _id = None
                    media = {}

                release_year_edit = dbc.Row(
                    [
                        dbc.Label("RELEASE YEAR", html_for="RELEASE_YEAR", width=2),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                min="1900",
                                id={"type": "edit-data", "index": "releaseYear"},
                                value=media["releaseYear"]
                                if "releaseYear" in media
                                else None,
                            ),
                            width=4,
                        ),
                        dbc.Label("EDITION YEAR", html_for="EDITION_YEAR", width=2),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                min="1900",
                                id={"type": "edit-data", "index": "editionYear"},
                                value=media["editionYear"]
                                if "editionYear" in media
                                else None,
                            ),
                            width=3,
                        ),
                    ],
                    className="mb-3",
                )

                artist_edit = dbc.Row(
                    [
                        dbc.Label("ARTIST", html_for="ARTIST", width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id={"type": "edit-data", "index": "artist"},
                                options=[
                                    {"label": str(i), "value": str(i)}
                                    for i in self.artists
                                ],
                                value=media["artist"] if "artist" in media else None,
                                optionHeight=40,
                                clearable=False,
                            )
                            if len(self.medias) > 0
                            else dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "artist"},
                                value=media["artist"] if "artist" in media else None,
                            ),
                            width=7,
                            id={"type": "add_media", "index": "add_artist_col"},
                        ),
                        dbc.Col(
                            dbc.Button(
                                color="primary",
                                className="bi bi-plus-circle",
                                id={"type": "add_media", "index": "add_artist_btn"},
                            ),
                            width=1,
                        ),
                    ],
                    className="mb-3",
                )

                title_edit = dbc.Row(
                    [
                        dbc.Label("TITLE", html_for="TITLE", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                minlength="3",
                                id={"type": "edit-data", "index": "title"},
                                value=media["title"] if "title" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                media_edit = dbc.Row(
                    [
                        dbc.Label("MEDIA", html_for="MEDIA", width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id={"type": "edit-data", "index": "media"},
                                options=[
                                    {"label": str(i), "value": str(i)}
                                    for i in self.medias["media"]
                                ],
                                value=media["media"] if "media" in media else None,
                                optionHeight=40,
                                clearable=False,
                            )
                            if len(self.medias["media"]) > 0
                            else dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "media"},
                            ),
                            width=7,
                            id={"type": "add_media", "index": "add_media_col"},
                        ),
                        dbc.Col(
                            dbc.Button(
                                color="primary",
                                className="bi bi-plus-circle",
                                id={"type": "add_media", "index": "add_media_btn"},
                            ),
                            width=1,
                        ),
                    ],
                    className="mb-3",
                )

                purchase_edit = dbc.Row(
                    [
                        dbc.Label("PURCHASE", html_for="PURCHASE", width=2),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id={"type": "edit-data", "index": "purchase"},
                                min_date_allowed=date(1900, 8, 5),
                                max_date_allowed=datetime.now(),
                                initial_visible_month=datetime.now(),
                                display_format="DD/MM/YYYY",
                                date=media["purchase"] if "purchase" in media else None,
                                style={"border-radius": "0.5rem", "width": "100%"},
                            ),
                            width=4,
                        ),
                        dbc.Label("ORIGEM", html_for="ORIGIN", width=2),
                        dbc.Col(
                            dcc.Dropdown(
                                id={"type": "edit-data", "index": "origin"},
                                options=[
                                    {"label": str(i), "value": str(i)}
                                    for i in self.medias["origin"]
                                ],
                                value=media["origin"] if "origin" in media else None,
                                optionHeight=40,
                                clearable=False,
                            )
                            if len(self.medias["origin"]) > 0
                            else dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "origin"},
                                value=media["origin"] if "origin" in media else None,
                            ),
                            width=3,
                            id={"type": "add_media", "index": "add_origin_col"},
                        ),
                        dbc.Col(
                            dbc.Button(
                                color="primary",
                                className="bi bi-plus-circle",
                                id={"type": "add_media", "index": "add_origin_btn"},
                            ),
                            width=1,
                        ),
                    ],
                    className="mb-3",
                )

                ifpi_mastering_edit = dbc.Row(
                    [
                        dbc.Label("IFPI MASTERING", html_for="ifpiMastering", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "ifpiMastering"},
                                value=media["ifpiMastering"]
                                if "ifpiMastering" in media
                                else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                ifpi_mould_edit = dbc.Row(
                    [
                        dbc.Label("IFPI MOULD", html_for="ifpiMould", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "ifpiMould"},
                                value=media["ifpiMould"]
                                if "ifpiMould" in media
                                else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                barcode_edit = dbc.Row(
                    [
                        dbc.Label("BARCODE", html_for="barcode", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "barcode"},
                                value=media["barcode"] if "barcode" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                lote_edit = dbc.Row(
                    [
                        dbc.Label("LOTE", html_for="lote", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={"type": "edit-data", "index": "lote"},
                                value=media["lote"] if "lote" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                matriz_edit = dbc.Row(
                    [
                        dbc.Label("MATRIZ", html_for="matriz", width=4),
                        dbc.Col(
                            dbc.Textarea(
                                id={"type": "edit-data", "index": "matriz"},
                                value=media["matriz"] if "matriz" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )
                title = (
                    f"{media['artist']} - {media['title']}"
                    if media != {}
                    else "Nova Entrada"
                )
                body = dbc.Form(
                    [
                        title_edit,
                        artist_edit,
                        media_edit,
                        ifpi_mastering_edit,
                        ifpi_mould_edit,
                        barcode_edit,
                        matriz_edit,
                        lote_edit,
                        html.Hr(),
                        release_year_edit,
                        purchase_edit,
                    ]
                )
                return title, body, True, f"{media['id']}" if "id" in media else None
            else:
                return "", "", False, ""

        @app.callback(
            Output("df", "data"),
            Input("edit-btn", "n_clicks"),
            Input("confirma_btn", "n_clicks"),
            State({"type": "edit-data", "index": ALL}, "value"),
            State({"type": "edit-data", "index": ALL}, "date"),
            State({"type": "edit-data", "index": ALL}, "id"),
            State("edit_id", "data"),
            prevent_initial_call=True,
        )
        def replace_on(n_clicks, n_clicks2, data, date, _id, item_id):
            cxt = callback_context.triggered
            prop_id = cxt[0]["prop_id"].split(".")[0]
            if prop_id == "confirma_btn":
                return True
            if prop_id == "edit-btn":
                edit = {}
                for x, i in enumerate(_id):
                    edit[i["index"]] = data[x]
                try:
                    edit["purchase"] = [x for x in date if x is not None][0]
                except Exception:
                    edit["purchase"] = None
                condition = [
                    edit["artist"] is not None,
                    edit["title"] is not None,
                    edit["media"] is not None,
                ]
                if all(condition):
                    if item_id is not None and item_id != "":
                        edit["id"] = item_id
                        result = requests.post(
                            environ["DB_API"] + "update/album",
                            headers=self.headers,
                            json=edit,
                        ).json()
                        print("ID", result["Message"])
                    else:
                        result = requests.post(
                            environ["DB_API"] + "new/album",
                            headers=self.headers,
                            json=edit,
                        ).json()
                        print("ID", result["Message"])
                    return True
                else:
                    return no_update
            else:
                return no_update

        @app.callback(
            Output("modal_delete", "is_open"),
            Output("delete_id", "data"),
            Input({"type": "delete_button", "index": ALL}, "n_clicks"),
            Input("confirma_btn", "n_clicks"),
            Input("cancela_btn", "n_clicks"),
            State("delete_id", "data"),
            prevent_initial_call=True,
        )
        def toggle_modal(_, confirma, cancela, item_id):
            cxt = callback_context.triggered
            _id = cxt[0]["prop_id"].split(".")[0]
            if _id == "confirma_btn":
                result = requests.post(
                    environ["DB_API"] + "delete/album",
                    headers=self.headers,
                    json={"id": item_id},
                ).json()
                print("Deleted: ", result["Message"])
                return False, ""
            if _id == "cancela_btn":
                return False, ""
            if cxt[0]["value"]:
                return True, loads(_id)["index"]
            return False, ""

        @app.callback(
            Output({"type": "add_media", "index": "add_media_col"}, "children"),
            Input({"type": "add_media", "index": "add_media_btn"}, "n_clicks"),
            prevent_initial_call=True,
        )
        def update_options(n_clicks):
            if n_clicks:
                return dbc.Input(
                    type="text",
                    id={"type": "edit-data", "index": "media"},
                    placeholder="Digite a Media",
                )

        @app.callback(
            Output({"type": "add_media", "index": "add_artist_col"}, "children"),
            Input({"type": "add_media", "index": "add_artist_btn"}, "n_clicks"),
            prevent_initial_call=True,
        )
        def update_options(n_clicks):
            if n_clicks:
                return dbc.Input(
                    type="text",
                    id={"type": "edit-data", "index": "artist"},
                    placeholder="Digite o Artista",
                )

        @app.callback(
            Output({"type": "add_media", "index": "add_origin_col"}, "children"),
            Input({"type": "add_media", "index": "add_origin_btn"}, "n_clicks"),
            prevent_initial_call=True,
        )
        def update_options(n_clicks):
            if n_clicks:
                return dbc.Input(
                    type="text",
                    id={"type": "edit-data", "index": "origin"},
                    placeholder="Digite a Origem",
                )
