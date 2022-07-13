from dash import html, dcc, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
from server import app
from json import loads


class Content:

    def __init__(self, conn):
        self.conn = conn

    def layout(self):
        return html.Div([
            dbc.Tabs(
                [
                    dbc.Tab([
                        dcc.Loading([
                            html.Div(id='disco'),
                            html.Hr(),
                            dbc.Row([
                                dbc.Col(
                                    dbc.Pagination(
                                        id="pagination",
                                        max_value=1,
                                        fully_expanded=False), width=3
                                )],
                                justify="center"
                            )
                        ]
                        ),
                    ], label="Lista"
                    ),
                    dbc.Tab(dbc.Col(
                        dcc.Graph(
                            id='total_year_graph'
                        ), width=12
                    ), label="Ano de Lançamento"),
                    dbc.Tab(dbc.Col(
                        dcc.Graph(
                            id='total_purchase_graph'
                        ), width=12
                    ), label="Ano de Aquisição"),
                ]
            )
        ], className='custom-content'
        )

    def callbacks(self):
        @app.callback(
            Output("total_year_graph", 'figure'),
            Output("total_purchase_graph", 'figure'),
            Input('df', 'data'),
            Input('filter_contents', 'data'),
        )
        def render(value, _filter):
            if _filter:
                _query = ""
                for key, value in _filter.items():
                    _query += f"{key} == '{value}' & "

                _query = _query[:_query.rfind("&")]
                df = self.conn.qyery("CD").query(_query)
            else:
                df = self.conn.qyery("CD")
            total_year = px.bar(df.groupby(['RELEASE_YEAR'])['RELEASE_YEAR'].count(),
                                labels={
                "index": "Ano",
                "value": "Total"
            },
                title="Ano de Lançamento",
                text_auto=True,
                height=600
            )
            total_year.update_layout(showlegend=False, hovermode="x unified")
            total_year.update_traces(
                hovertemplate='Total: %{y}<extra></extra>')

            total_purchase = px.bar(df.groupby(df['PURCHASE'].dt.year)['PURCHASE'].count(),
                                    labels={
                "index": "Ano",
                "value": "Total"
            },
                title="Ano de Aquisição",
                text_auto=True,
                height=600
            ).update_layout(showlegend=False)
            return total_year, total_purchase

        @app.callback(
            Output('disco', 'children'),
            Output('filter_contents', 'data'),
            Output('pagination', 'max_value'),
            Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
            Input('pagination_contents', 'data'),
            Input('df', 'data'),
            State('filter_contents', 'data'),
            prevent_initial_callback=True)
        def update_output(value, pagination, _, _filter):
            df = self.conn.qyery("CD")
            cxt = callback_context.triggered
            _artist = df.groupby('ARTIST', as_index=False)     
            if not any(value):
                if cxt[0]['value'] == None:
                    try:
                        _filter.pop(
                            loads(cxt[0]['prop_id'].split('.')[0])["index"]
                        )
                    except:
                        pass
                max_index = int(len(_artist.groups.keys())/10)
                if max_index > 10:
                    artists = list(_artist.groups.keys())[
                        (pagination*10)-10:pagination*10]
                    dff = df.query(
                        f"ARTIST == @artists").groupby('ARTIST', as_index=False)
                else:
                    dff = df.groupby('ARTIST', as_index=False)
            else:
                dff = df
                if cxt[0]['prop_id'].split('.')[0] not in ["pagination_contents","df"]:
                    _filter_index = loads(
                        cxt[0]['prop_id'].split('.')[0])["index"]
                    _filter[_filter_index] = cxt[0]["value"]
                    _filter = dict((k, v)
                                   for k, v in _filter.items() if v is not None)
                _query = ""
                for key, value in _filter.items():
                    _query += f"{key} == '{value}' & "

                _query = _query[:_query.rfind("&")]
                _artist = df.query(_query).groupby(
                    'ARTIST', as_index=False)
                artists = list(_artist.groups.keys())[
                    (pagination*10)-10:pagination*10]
                dff = df.query(
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
                                        html.Div(f' PURCHASE: {row["PURCHASE"].strftime("%d/%m/%Y")}', className="bi bi-cart3")),
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
