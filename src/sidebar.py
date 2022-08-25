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
                        html.Div(id="media_totals"),
                        html.Hr()
                    ]
                )
            ],
            className="custom-sidebar"
        )

    def callbacks(self):
        @app.callback(
            Output("media_totals", 'children'),
            Input('df', 'data')
        )
        def render(value):
            df = self.conn.qyery("CD")

            table_header = [
                html.Thead(html.Tr([html.Th("MEDIA"), html.Th("QUANTIDADE")]))
            ]
            rows = [
                html.Tr([html.Td(i), html.Td(
                    len(df.query(f"MEDIA=='{i}'").index))])
                for i in sorted(df['MEDIA'].unique())
            ]
            table_body = [html.Tbody(rows, className="g-2")]
            return dbc.Table(table_header + table_body, bordered=True)

        @ app.callback(
            Output("drop", 'children'),
            Input('filter_contents', 'data'),
            prevent_initial_call=True
        )
        def toggle_modal(_filter):
            df = self.conn.qyery("CD")
            if _filter != {}:
                _query = ""
                for key, value in _filter.items():
                    _query += f"""{key} == "{value}" & """

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
