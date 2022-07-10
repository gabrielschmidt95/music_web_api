from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px


class Content:

    def __init__(self, df):
        self.df = df

    def total_year(self):
        return dbc.Col(
            dcc.Graph(
                id='total_year_graph',
                figure=px.bar(self.df.groupby(['RELEASE_YEAR'])['RELEASE_YEAR'].count(),
                              labels={
                    "index": "Ano",
                    "value": "Total"
                },
                    title="Ano de Lançamento",
                    text_auto=True,
                    height=600
                ).update_layout(showlegend=False, hovermode="x unified")
                .update_traces(hovertemplate='Total: %{y}<extra></extra>')
            ), width=12
        )

    def total_buy(self):
        return dbc.Col(
            dcc.Graph(
                id='total_purchase_graph',
                figure=px.bar(self.df.groupby(self.df['PURCHASE'].dt.year)['PURCHASE'].count(),
                              labels={
                    "index": "Ano",
                    "value": "Total"
                },
                    title="Ano de Aquisição",
                    text_auto=True,
                    height=600
                ).update_layout(showlegend=False)
            ), width=12
        )

    def content(self):
        return html.Div([
            dbc.Tabs(
                [
                    dbc.Tab([
                        dcc.Loading(html.Div(id='disco')),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(
                                dbc.Pagination(
                                    id="pagination",
                                    max_value=1,
                                    fully_expanded=False), width=3
                            )], justify="center"
                        )], label="Lista"
                    ),
                    dbc.Tab(self.total_year(), label="Ano de Lançamento"),
                    dbc.Tab(self.total_buy(), label="Ano de Aquisição"),
                ]
            )
        ], className='custom-content'
        )
