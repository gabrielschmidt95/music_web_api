from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from server import app


class Sidebar:

    def __init__(self, conn):
        self.conn = conn

    def layout(self):
        return dbc.Col(
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
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("CD\'s"),
                                            dbc.CardBody(
                                                html.H5("", className="card-title", id="cds_total")),
                                        ], color="success", outline=True
                                    )
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("LP\'s"),
                                            dbc.CardBody(
                                                html.H5("", className="card-title", id="lps_total")),
                                        ], color="success", outline=True
                                    )
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("DVD\'s"),
                                            dbc.CardBody(
                                                html.H5("", className="card-title", id="dvds_total")),
                                        ], color="success", outline=True
                                    )
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("BL\'s"),
                                            dbc.CardBody(
                                                html.H5("", className="card-title", id="bls_total")),
                                        ], color="success", outline=True
                                    )
                                )
                            ],
                            className="g-2",
                        ),
                        html.Hr(),
                        dbc.Row(
                            [
                                dcc.Download(id="download_xlsx"),
                                dbc.Col(
                                    dbc.Button(
                                        "Donwload XLSX",
                                        color="success",
                                        className="me-1",
                                        id="download_xlsx_btn"
                                    ),
                                    width=12
                                ),
                            ],
                            className="g-2",
                        )
                    ]
                )
            ],
            className="custom-sidebar"
        )

    def callbacks(self):
        @app.callback(
            Output("cds_total", 'children'),
            Output("lps_total", 'children'),
            Output("dvds_total", 'children'),
            Output("bls_total", 'children'),
            Input('df', 'data')
        )
        def render(value):
            df = self.conn.qyery("CD")
            cds = len(df.query("MEDIA=='CD'").index)
            lps = len(df.query("MEDIA=='LP'").index)
            dvds = len(df.query("MEDIA=='DVD'").index)
            bls = len(df.query("MEDIA=='BL'").index)
            return cds, lps, dvds, bls

        @app.callback(
            Output("drop", 'children'),
            Input('filter_contents', 'data'),
            prevent_initial_call=True
        )
        def toggle_modal(_filter):
            df = self.conn.qyery("CD")
            print(_filter)
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
                    dbc.Label(" Media", width=3, className="bi bi-disc"),
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
                                     for i in sorted(dff['ORIGIN'].dropna().unique())],
                            value=_filter["ORIGIN"] if "ORIGIN" in _filter else None,
                            className="me-3"
                        ), width=9
                    ),
                ],
                className="g-2",
            )]

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
                return dcc.send_data_frame(df.to_excel, "collection.xlsx")
