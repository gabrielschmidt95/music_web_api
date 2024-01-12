from datetime import date, datetime
from json import loads
from os import environ

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback_context, dcc, html, no_update

from server import app
from api.db_api import DBApi
from api.discogs import get_data_by_id


class DataModal:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + environ["OAUTH_TOKEN"],
        }
        self.api = DBApi()
        self.medias = self.api.get("medias")
        self.artists = self.api.get("artists")

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
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Discogs Id")),
                        dbc.ModalBody(
                            dbc.Input(
                                type="text",
                                id="discogs_input",
                                placeholder="Digite o ID do Discogs",
                            ),
                            id="modal_discogs_body",
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Confirma",
                                    id="confirma_discogs",
                                    className="ms-auto",
                                    n_clicks=0,
                                ),
                                dbc.Button(
                                    "Cancela",
                                    id="cancela_discogs",
                                    className="ms-auto",
                                    n_clicks=0,
                                ),
                            ]
                        ),
                    ],
                    is_open=False,
                    id="modal_discogs",
                ),
            ]
        )

    def form_layout(self, media: dict) -> dbc.Form:
        release_year_edit = dbc.Row(
            [
                dbc.Label("RELEASE YEAR", html_for="RELEASE_YEAR", width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        min="1900",
                        id={"type": "edit-data", "index": "releaseYear"},
                        value=media["releaseYear"] if "releaseYear" in media else None,
                    ),
                    width=4,
                ),
                dbc.Label("EDITION YEAR", html_for="EDITION_YEAR", width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        min="1900",
                        id={"type": "edit-data", "index": "editionYear"},
                        value=media["editionYear"] if "editionYear" in media else None,
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
                            {"label": str(i), "value": str(i)} for i in self.artists
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

        if "origin" not in media:
            media["origin"] = None
            media["media"] = None

        media_edit = dbc.Row(
            [
                dbc.Label("MEDIA", html_for="MEDIA", width=4),
                dbc.Col(
                    dcc.Dropdown(
                        id={"type": "edit-data", "index": "media"},
                        options=[
                            {"label": str(i), "value": str(i)}
                            for i in self.medias["media"]
                            if self.medias["media"] is not None
                        ],
                        value=media["media"],
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
                        value=media["origin"],
                        optionHeight=40,
                        clearable=False,
                    )
                    if len(self.medias["origin"]) > 0
                    else dbc.Input(
                        type="text",
                        id={"type": "edit-data", "index": "origin"},
                        value=media["origin"],
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
                        value=media["ifpiMould"] if "ifpiMould" in media else None,
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
        return dbc.Form(
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
                    media = self.api.post("album/id", {"id": _id})

                except Exception:
                    _id = None
                    media = {}

                title = (
                    f"{media['artist']} - {media['title']}"
                    if media != {}
                    else "Nova Entrada"
                )
                body = self.form_layout(media)

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
                    edit["title"] = edit["title"].upper()
                    edit["artist"] = edit["artist"].upper()
                    if item_id is not None and item_id != "":
                        edit["id"] = item_id
                        result = self.api.post("update/album", edit)
                        print("ID", result["Message"])
                    else:
                        result = self.api.post("new/album", edit)
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
                result = self.api.post("delete/album", {"id": item_id})
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

        @app.callback(
            Output("modal_discogs", "is_open"),
            Output("discogs_id", "data"),
            Input({"type": "fix_discogs", "index": ALL}, "n_clicks"),
            Input("cancela_discogs", "n_clicks"),
            Input("confirma_discogs", "n_clicks"),
            State("discogs_input", "value"),
            State("discogs_id", "data"),
            prevent_initial_call=True,
        )
        def toggle_modal(n_clicks, cancela, confirma, value, item_id):
            cxt = callback_context.triggered
            _id = cxt[0]["prop_id"].split(".")[0]
            if _id == "confirma_discogs":
                print("Updating Discogs ID: ", item_id)
                album = self.api.post("album/id", {"id": item_id})
                value = "".join(filter(str.isdigit, value))
                row = get_data_by_id(album, value)
                if not row:
                    return True, "Changed"

                result = self.api.post("update/album", row)
                print("Updating Discogs: ", result)
                return False, ""

            if _id == "cancela_discogs":
                return False, ""
            if cxt[0]["value"]:
                return True, loads(_id)["index"]
            return False, ""