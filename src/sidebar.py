from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
from json import loads
from server import app


class Sidebar:

    def __init__(self, df):
        self.df = df
    
    def render(self):
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
                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardHeader("CD\'s"),
                                        dbc.CardBody(
                                            [
                                                html.H5(len(self.df.query("MEDIA=='CD'").index),
                                                        className="card-title"),
                                            ]
                                        ),
                                    ], color="success", outline=True)
                                ),
                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardHeader("LP\'s"),
                                        dbc.CardBody(
                                            [
                                                html.H5(len(self.df.query("MEDIA=='LP'").index),
                                                        className="card-title"),
                                            ]
                                        ),
                                    ], color="success", outline=True)
                                ),
                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardHeader("DVD\'s"),
                                        dbc.CardBody(
                                            [
                                                html.H5(len(self.df.query("MEDIA=='DVD'").index),
                                                        className="card-title"),
                                            ]
                                        ),
                                    ], color="success", outline=True)
                                ),
                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardHeader("BL\'s"),
                                        dbc.CardBody(
                                            [
                                                html.H5(len(self.df.query("MEDIA=='BL'").index),
                                                        className="card-title"),
                                            ]
                                        ),
                                    ], color="success", outline=True)
                                )
                            ],
                            className="g-2",
                        ),
                        html.Hr(),
                        dbc.Row(
                            [
                                dcc.Download(id="download_xlsx"),
                                dbc.Col(
                                    dbc.Button("Donwload XLSX", color="success", className="me-1", id="download_xlsx_btn"), width=12
                                ),
                            ],
                            className="g-2",
                        ),

                    ])
            ],
            className="custom-sidebar"
        )

    def filters(self):
        @app.callback(
            Output("drop", 'children'),
            Input('filter_contents', 'data'),
            prevent_initial_call=True
        )
        def toggle_modal(_filter):
            if _filter != {}:
                _query = ""
                for key, value in _filter.items():
                    _query += f"{key} == '{value}' & "

                _query = _query[:_query.rfind("&")]
                dff = self.df.query(_query)
            else:
                dff = self.df
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
            Output('disco', 'children'),
            Output('filter_contents', 'data'),
            Output('pagination', 'max_value'),
            Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
            Input('pagination_contents', 'data'),
            State('filter_contents', 'data'),
            prevent_initial_callback=True)
        def update_output(value, pagination, _filter):
            cxt = callback_context.triggered
            _artist = self.df.groupby('ARTIST', as_index=False)
            if not any(value):
                if cxt[0]['prop_id'] != '.':
                    _filter.pop(loads(cxt[0]['prop_id'].split('.')[0])["index"])
                max_index = int(len(_artist.groups.keys())/10)
                if max_index > 10:
                    artists = list(_artist.groups.keys())[
                        (pagination*10)-10:pagination*10]
                    dff = self.df.query(
                        f"ARTIST == @artists").groupby('ARTIST', as_index=False)
                else:
                    dff = self.df.groupby('ARTIST', as_index=False)
            else:
                dff = self.df
                if cxt[0]['prop_id'].split('.')[0] != "pagination_contents":
                    _filter_index = loads(cxt[0]['prop_id'].split('.')[0])["index"]
                    _filter[_filter_index] = cxt[0]["value"]
                    _filter = dict((k, v) for k, v in _filter.items() if v is not None)
                _query = ""
                for key, value in _filter.items():
                    _query += f"{key} == '{value}' & "

                _query = _query[:_query.rfind("&")]
                _artist = self.df.query(_query).groupby('ARTIST', as_index=False)
                artists = list(_artist.groups.keys())[(pagination*10)-10:pagination*10]
                dff = self.df.query(
                    f"ARTIST == @artists").query(_query).groupby('ARTIST', as_index=False)
                max_index = int(len(_artist.groups.keys())/10)
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
                                    dbc.Col(html.Div(
                                        f' RELEASE YEAR: {row["RELEASE_YEAR"]}', className="bi bi-calendar-event")),
                                    dbc.Col(
                                        html.Div(f' MEDIA: {row["MEDIA"]}', className="bi bi-vinyl")),
                                    dbc.Col(
                                        html.Div(f' PURCHASE: {row["PURCHASE"]}', className="bi bi-cart3")),
                                ],
                                align="start",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(f' ORIGIN: {row["ORIGIN"]}', className="bi bi-house")),
                                    dbc.Col(
                                        html.Div(f' IFPI_MASTERING: {row["IFPI_MASTERING"]}', className="bi bi-body-text")),
                                    dbc.Col(
                                        html.Div(f' IFPI_MOULD: {row["IFPI_MOULD"]}', className="bi bi-body-text")),
                                ],
                                align="start",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(f' BARCODE: {row["BARCODE"]}', className="bi bi-body-text")),
                                    dbc.Col(
                                        html.Div(f' MATRIZ: {row["MATRIZ"]}', className="bi bi-body-text")),
                                    dbc.Col(
                                        html.Div(f' LOTE: {row["LOTE"]}', className="bi bi-body-text"))
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

                        ], title=f'{row["RELEASE_YEAR"]} - {row["TITLE"]}')
                        for row in group.sort_values("RELEASE_YEAR").to_dict('records')], start_collapsed=True)
                ], title=name,
                ) for name, group in dff], start_collapsed=True)
            return accord, _filter, max_index


        @app.callback(
            Output("pagination_contents", "data"),
            Input("pagination", "active_page"),
            prevent_initial_call=True
        )
        def change_page(page):
            if page:
                return page