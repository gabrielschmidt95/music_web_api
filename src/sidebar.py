import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from server import app
import requests
import os


class Sidebar:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + os.environ["OAUTH_TOKEN"],
        }

    def layout(self):
        return dbc.Col(
            [
                html.H2("Music", className="display-4", style={"color": "#0d6efd"}),
                html.Hr(),
                html.P("Collection Mananger", className="lead"),
                html.Hr(),
                dbc.Form(
                    [
                        html.Div(id="drop"),
                        html.Hr(),
                        html.Div(id="media_totals"),
                        html.Hr(),
                    ]
                ),
                dbc.Button(
                    "Logout",
                    id="logout",
                    color="danger",
                    className="me-1",
                    style={"width": "100%"},
                ),
            ],
            className="custom-sidebar",
        )

    def callbacks(self):
        @app.callback(Output("media_totals", "children"), Input("df", "data"))
        def render(value):
            totals = requests.get(
                os.environ["DB_API"] + "totals", headers=self.headers
            ).json()

            table_header = [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("MEDIA", style={"color": "#0d6efd"}),
                            html.Th("QUANTIDADE", style={"color": "#0d6efd"}),
                        ]
                    )
                )
            ]
            rows = [
                html.Tr([html.Td(_type), html.Td(value)])
                for _type, value in totals["media"].items()
            ]
            table_body = [html.Tbody(rows, className="g-2")]
            return dbc.Table(table_header + table_body, bordered=True)

        @app.callback(
            Output("drop", "children"),
            Input("filter_contents", "data"),
            Input("url", "pathname"),
            prevent_initial_call=True,
        )
        def toggle_modal(_filter, _):
            artist = requests.get(
                os.environ["DB_API"] + "artists", headers=self.headers
            ).json()

            medias = requests.get(
                os.environ["DB_API"] + "medias", headers=self.headers
            ).json()

            return [
                dbc.Row(
                    [
                        dbc.Label(" Artista", width=3, className="bi bi-person"),
                        dbc.Col(
                            dcc.Dropdown(
                                id={"type": "filter-dropdown", "index": "ARTIST"},
                                options=[
                                    {"label": str(i), "value": str(i)}
                                    for i in sorted(artist)
                                ],
                                value=_filter["ARTIST"]
                                if "ARTIST" in _filter
                                else None,
                                optionHeight=40,
                                className="me-3",
                            ),
                            width=9,
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
                                id={"type": "filter-dropdown", "index": "MEDIA"},
                                options=[
                                    {"label": str(i), "value": str(i)}
                                    for i in sorted(medias["media"])
                                ],
                                value=_filter["MEDIA"] if "MEDIA" in _filter else None,
                                className="me-3",
                            ),
                            width=9,
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
                                id={"type": "filter-dropdown", "index": "ORIGIN"},
                                options=[
                                    {"label": str(i), "value": str(i)}
                                    for i in sorted(
                                        medias["origin"]
                                    )
                                ],
                                value=_filter["ORIGIN"]
                                if "ORIGIN" in _filter
                                else None,
                                className="me-3",
                            ),
                            width=9,
                        ),
                    ],
                    className="g-2",
                ),
            ]

        @app.callback(
            Output("logout", "children"),
            Input("logout", "n_clicks"),
            prevent_initial_call=True,
        )
        def update_output(n_clicks):
            if n_clicks:
                return dcc.Location(pathname="/logout", id="logout")
