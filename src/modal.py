from dash import dcc, Input, Output, State, callback_context, ALL, MATCH, html, no_update
import dash_bootstrap_components as dbc
from datetime import datetime, date
from server import app
from json import loads


class Data_Modal:

    def __init__(self, conn):
        self.conn = conn

    def layout(self):
        return dbc.Col([
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(id="modal_edit_title")),
                    dbc.ModalBody(id="modal_edit_body"),
                    dbc.ModalFooter(dbc.Button(
                        "Salvar", id='edit-btn', className="ms-auto", n_clicks=0
                    )),
                ],
                is_open=False, id='modal_edit', size="lg"
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Deseja Apagar?")
                    ),
                    dbc.ModalBody(id="modal_delete_body"),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Confirma", id='confirma_btn', className="ms-auto", n_clicks=0
                        ),
                        dbc.Button(
                            "Cancela", id='cancela_btn', className="ms-auto", n_clicks=0
                        )
                    ]),
                ],
                is_open=False, id='modal_delete'
            )
        ])

    def callbacks(self):
        @app.callback(
            Output("modal_edit_title", "children"),
            Output("modal_edit_body", "children"),
            Output("modal_edit", "is_open"),
            Output("edit_id", "data"),
            Input("edit-btn", "n_clicks"),
            Input("insert_btn", "n_clicks"),
            Input({'type': 'edit_button', 'index': ALL}, 'n_clicks'),
            prevent_initial_call=True
        )
        def fill_edit_modal(edit_btn,insert_btn, value):
            cxt = callback_context.triggered
            if cxt[0]['prop_id'] == 'edit-btn.n_clicks':
                return "", "", False, None
            if cxt[0]['value']:
                try:
                    _id = loads(cxt[0]['prop_id'].split('.')[0])["index"]
                    media = self.conn.find_one("CD", _id)
                except:
                    _id = None
                    media = {}
                release_year_edit = dbc.Row(
                    [
                        dbc.Label("RELEASE YEAR",
                                  html_for="RELEASE_YEAR", width=2),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                min="1900",
                                id={'type': 'edit-data',
                                    'index': "RELEASE_YEAR"},
                                value=media["RELEASE_YEAR"] if "RELEASE_YEAR" in media else None,
                            ),
                            width=4,
                        ),
                        dbc.Label("EDITION YEAR",
                                  html_for="EDITION_YEAR", width=2),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                min="1900",
                                id={'type': 'edit-data',
                                    'index': "EDITION_YEAR"},
                                value=media["EDITION_YEAR"] if "EDITION_YEAR" in media else None,
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
                                id={'type': 'edit-data', 'index': "ARTIST"},
                                options=[
                                    {'label': str(i), 'value': str(i)}
                                    for i in sorted(self.conn.qyery("CD")['ARTIST'].unique())],
                                value=media["ARTIST"] if "ARTIST" in media else None,
                                optionHeight=40,
                                clearable=False,
                            ) if len(self.conn.qyery("CD")['MEDIA'].unique()) > 0 else dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "ARTIST"},
                                value=media["ARTIST"] if "ARTIST" in media else None,
                            ),
                            width=7, id={'type': 'add_media', 'index': "add_artist_col"}
                        ),
                        dbc.Col(
                            dbc.Button(color="primary", className="bi bi-plus-circle", id={'type': 'add_media', 'index': "add_artist_btn"}), width=1
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
                                id={'type': 'edit-data', 'index': "TITLE"},
                                value=media["TITLE"] if "TITLE" in media else None,
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
                                id={'type': 'edit-data', 'index': "MEDIA"},
                                options=[
                                    {'label': str(i), 'value': str(i)}
                                    for i in sorted(self.conn.qyery("CD")['MEDIA'].unique())],
                                value=media["MEDIA"] if "MEDIA" in media else None,
                                optionHeight=40,
                                clearable=False,
                            ) if len(self.conn.qyery("CD")['MEDIA'].unique()) > 0 else dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "MEDIA"},
                            ),
                            width=7, id={'type': 'add_media', 'index': "add_media_col"}
                        ),
                        dbc.Col(
                            dbc.Button(color="primary", className="bi bi-plus-circle", id={'type': 'add_media', 'index': "add_media_btn"}), width=1
                        ),
                    ],
                    className="mb-3",
                )

                purchase_edit = dbc.Row(
                    [
                        dbc.Label("PURCHASE", html_for="PURCHASE", width=2),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id={'type': 'edit-data', 'index': 'PURCHASE'},
                                min_date_allowed=date(1900, 8, 5),
                                max_date_allowed=datetime.now(),
                                initial_visible_month=datetime.now(),
                                display_format='DD/MM/YYYY',
                                date=media["PURCHASE"] if "PURCHASE" in media else None,
                                style={"border-radius": "0.5rem",
                                       "width": "100%"}
                            ),
                            width=4,
                        ),
                        dbc.Label("ORIGEM", html_for="ORIGIN", width=2),
                        dbc.Col(
                            dcc.Dropdown(
                                id={'type': 'edit-data', 'index': "ORIGIN"},
                                options=[
                                    {'label': str(i), 'value': str(i)}
                                    for i in sorted(self.conn.qyery("CD")['ORIGIN'].unique())],
                                value=media["ORIGIN"] if "ORIGIN" in media else None,
                                optionHeight=40,
                                clearable=False,
                            ) if len(self.conn.qyery("CD")['MEDIA'].unique()) > 0 else dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "ORIGIN"},
                                value=media["ORIGIN"] if "ORIGIN" in media else None,
                            ),
                            width=3, id={'type': 'add_media', 'index': "add_origin_col"}
                        ),
                        dbc.Col(
                            dbc.Button(color="primary", className="bi bi-plus-circle", id={'type': 'add_media', 'index': "add_origin_btn"}), width=1
                        ),
                    ],
                    className="mb-3",
                )

                ifpi_mastering_edit = dbc.Row(
                    [
                        dbc.Label("IFPI MASTERING",
                                  html_for="IFPI_MASTERING", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data',
                                    'index': "IFPI_MASTERING"},
                                value=media["IFPI_MASTERING"] if "IFPI_MASTERING" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                ifpi_mould_edit = dbc.Row(
                    [
                        dbc.Label("IFPI MOULD",
                                  html_for="IFPI_MOULD", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "IFPI_MOULD"},
                                value=media["IFPI_MOULD"] if "IFPI_MOULD" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                barcode_edit = dbc.Row(
                    [
                        dbc.Label("BARCODE", html_for="BARCODE", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "BARCODE"},
                                value=media["BARCODE"] if "BARCODE" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                lote_edit = dbc.Row(
                    [
                        dbc.Label("LOTE", html_for="LOTE", width=4),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "LOTE"},
                                value=media["LOTE"] if "LOTE" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )

                matriz_edit = dbc.Row(
                    [
                        dbc.Label("MATRIZ", html_for="MATRIZ", width=4),
                        dbc.Col(
                            dbc.Textarea(
                                id={'type': 'edit-data', 'index': "MATRIZ"},
                                value=media["MATRIZ"] if "MATRIZ" in media else None,
                            ),
                            width=7,
                        ),
                    ],
                    className="mb-3",
                )
                title = f"{media['ARTIST']} - {media['TITLE']}" if media != {} else "Nova Entrada"
                body = dbc.Form([
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
                ])
                return title, body, True, f"{media['_id']}" if "_id" in media else None
            else:
                return "", "", False, ""

        @app.callback(
            Output("df", "data"),
            Input("edit-btn", "n_clicks"),
            Input("confirma_btn", "n_clicks"),
            State({'type': 'edit-data', 'index': ALL}, "value"),
            State({'type': 'edit-data', 'index': ALL}, "date"),
            State({'type': 'edit-data', 'index': ALL}, "id"),
            State("edit_id", "data"),
            prevent_initial_call=True
        )
        def replace_on(n_clicks, n_clicks2, data, date, _id, item_id):
            cxt = callback_context.triggered
            prop_id = cxt[0]['prop_id'].split('.')[0]
            if prop_id == 'confirma_btn':
                return True
            if prop_id == 'edit-btn':
                edit = {}
                for x, i in enumerate(_id):
                    edit[i['index']] = data[x]
                try:
                    edit['PURCHASE'] = [x for x in date if x is not None][0]
                except:
                    edit['PURCHASE'] = None
                condition = [
                    edit['ARTIST'] is not None,
                    edit['TITLE'] is not None,
                    edit['MEDIA'] is not None,
                ]
                if all(condition):
                    if item_id is not None and item_id != '':
                        self.conn.replace_one("CD", item_id, edit)
                    else:
                        self.conn.insert_one("CD", edit)
                    return True
                else:
                    return no_update
            else:
                return no_update

        @app.callback(
            Output("modal_delete", "is_open"),
            Output("delete_id", "data"),
            Input({'type': 'delete_button', 'index': ALL}, 'n_clicks'),
            Input("confirma_btn", "n_clicks"),
            Input("cancela_btn", "n_clicks"),
            State("delete_id", "data"),
            prevent_initial_call=True
        )
        def toggle_modal(_, confirma, cancela, item_id):
            cxt = callback_context.triggered
            _id = cxt[0]['prop_id'].split('.')[0]
            if _id == "confirma_btn":
                self.conn.delete_one("CD", item_id)
                return False, ""
            if _id == "cancela_btn":
                return False, ""
            if cxt[0]['value']:
                return True, loads(_id)["index"]
            return False, ""

        @app.callback(
            Output({'type': 'add_media', 'index': "add_media_col"}, 'children'),
            Input({'type': 'add_media', 'index': "add_media_btn"}, 'n_clicks'),
            prevent_initial_call=True
        )
        def update_options(n_clicks):
            if n_clicks:
                return dbc.Input(
                    type="text",
                    id={'type': 'edit-data', 'index': "MEDIA"},
                    placeholder="Digite a Media"
                )

        @app.callback(
            Output({'type': 'add_media', 'index': "add_artist_col"}, 'children'),
            Input({'type': 'add_media', 'index': "add_artist_btn"}, 'n_clicks'),
            prevent_initial_call=True
        )
        def update_options(n_clicks):
            if n_clicks:
                return dbc.Input(
                    type="text",
                    id={'type': 'edit-data', 'index': "ARTIST"},
                    placeholder="Digite o Artista"
                )
        
        @app.callback(
            Output({'type': 'add_media', 'index': "add_origin_col"}, 'children'),
            Input({'type': 'add_media', 'index': "add_origin_btn"}, 'n_clicks'),
            prevent_initial_call=True
        )
        def update_options(n_clicks):
            if n_clicks:
                return dbc.Input(
                    type="text",
                    id={'type': 'edit-data', 'index': "ORIGIN"},
                    placeholder="Digite a Origem"
                )

