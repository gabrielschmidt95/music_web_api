from dash import dcc, Input, Output, State, callback_context, ALL, MATCH
from server import app
from json import loads
from datetime import datetime, date
import dash_bootstrap_components as dbc

class Data_Modal:

    def __init__(self, df, conn):
        self.conn = conn
        self.df = df

    def render(self):
        @app.callback(
            Output({'type': 'edit-data', 'index': MATCH}, "children"),
            Input({'type': 'edit-data', 'index': MATCH}, "n_clicks"),
            State({'type': 'edit-data', 'index': ALL}, "value"),
            State({'type': 'edit-data', 'index': ALL}, "id"),
            prevent_initial_call=True
        )
        def toggle_modal(value, data, _id):
            cxt = callback_context.triggered
            edit = {}
            id = loads(cxt[0]['prop_id'].split('.')[0])["index"]
            for x, i in enumerate(_id):
                edit[i['index']] = data[x]

            del edit[id]
            self.conn.replace_one("CD", id, edit)
            return "Salvo!"

        @app.callback(
            Output("modal", "children"),
            Input({'type': 'edit_button', 'index': ALL}, 'n_clicks'),
            prevent_initial_call=True
        )
        def toggle_modal(value):
            cxt = callback_context.triggered
            if cxt[0]['value']:
                _id = loads(cxt[0]['prop_id'].split('.')[0])["index"]
                media = self.conn.find_one("CD", _id)
                release_year_edit = dbc.Row(
                    [
                        dbc.Label("RELEASE YEAR",
                                  html_for="RELEASE_YEAR", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                id={'type': 'edit-data',
                                    'index': "RELEASE_YEAR"},
                                value=media["RELEASE_YEAR"] if "RELEASE_YEAR" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                artist_edit = dbc.Row(
                    [
                        dbc.Label("ARTIST", html_for="ARTIST", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "ARTIST"},
                                value=media["ARTIST"] if "ARTIST" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                title_edit = dbc.Row(
                    [
                        dbc.Label("ARTIST", html_for="TITLE", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "TITLE"},
                                value=media["TITLE"] if "TITLE" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                media_edit = dbc.Row(
                    [
                        dbc.Label("MEDIA", html_for="MEDIA", width=6),
                        dbc.Col(
                            dcc.Dropdown(
                                id={'type': 'edit-data', 'index': "MEDIA"},
                                options=[{'label': str(i), 'value': str(i)}
                                         for i in sorted(self.df['MEDIA'].unique())],
                                value=media["MEDIA"] if "MEDIA" in media else None,
                                optionHeight=40,
                                clearable=False,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                purchase_edit = dbc.Row(
                    [
                        dbc.Label("PURCHASE", html_for="PURCHASE", width=6),
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
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                origin_edit = dbc.Row(
                    [
                        dbc.Label("ORIGEM", html_for="ORIGIN", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "ORIGIN"},
                                value=media["ORIGIN"] if "ORIGIN" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                edition_year_edit = dbc.Row(
                    [
                        dbc.Label("EDITION YEAR",
                                  html_for="EDITION_YEAR", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                id={'type': 'edit-data',
                                    'index': "EDITION_YEAR"},
                                value=media["EDITION_YEAR"] if "EDITION_YEAR" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                ifpi_mastering_edit = dbc.Row(
                    [
                        dbc.Label("IFPI MASTERING",
                                  html_for="IFPI_MASTERING", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data',
                                    'index': "IFPI_MASTERING"},
                                value=media["IFPI_MASTERING"] if "IFPI_MASTERING" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                ifpi_mould_edit = dbc.Row(
                    [
                        dbc.Label("IFPI MOULD",
                                  html_for="IFPI_MOULD", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "IFPI_MOULD"},
                                value=media["IFPI_MOULD"] if "IFPI_MOULD" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                barcode_edit = dbc.Row(
                    [
                        dbc.Label("BARCODE", html_for="BARCODE", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "BARCODE"},
                                value=media["BARCODE"] if "BARCODE" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                lote_edit = dbc.Row(
                    [
                        dbc.Label("LOTE", html_for="LOTE", width=6),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id={'type': 'edit-data', 'index': "LOTE"},
                                value=media["LOTE"] if "LOTE" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                matriz_edit = dbc.Row(
                    [
                        dbc.Label("MATRIZ", html_for="MATRIZ", width=6),
                        dbc.Col(
                            dbc.Textarea(
                                id={'type': 'edit-data', 'index': "MATRIZ"},
                                value=media["MATRIZ"] if "MATRIZ" in media else None,
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                )

                return dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(
                            f"{media['ARTIST']} - {media['TITLE']}")),
                        dbc.ModalBody(
                            dbc.Form([
                                release_year_edit,
                                artist_edit,
                                title_edit,
                                media_edit,
                                purchase_edit,
                                origin_edit,
                                edition_year_edit,
                                ifpi_mastering_edit,
                                ifpi_mould_edit,
                                barcode_edit,
                                matriz_edit,
                                lote_edit
                            ])
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Save", id={
                                    'type': 'edit-data',
                                    'index': f"{media['_id']}"
                                }, className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    is_open=True, id='modal'
                )
            else:
                return ""
